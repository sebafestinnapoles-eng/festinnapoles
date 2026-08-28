const SUPABASE_URL = "https://dpjyakzdobjmpkerhkik.supabase.co/rest/v1/reservas";
const DEFAULT_SUPABASE_ANON_KEY =
  "eyJhbGciOiJIUzI1NiIsInJlZiI6IkpXVCJ9.eyJpc3MiOiJzdWJhYmFzZSIsInJlZiI6ImRwanlha3pkb2JqbXBrZXJoa2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAzMDA4MDMsImV4cCI6MjA5NTg3NjgwM30.IVlRkWTlfVNqn9l1POy9F_yVpFpjWrhoFU_zLKOH_vs";

const RESEND_API_URL = "https://api.resend.com/emails";

function sendJson(response, statusCode, body) {
  response.statusCode = statusCode;
  response.setHeader("Content-Type", "application/json; charset=utf-8");
  response.end(JSON.stringify(body));
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function buildReservationEmail(payload) {
  const rows = [
    ["Origen", payload.origen === "landing" ? "Landing web Festín Nápoles" : payload.origen || "No especificado"],
    ["Nombre", payload.nombre],
    ["Fecha", payload.fecha_evento],
    ["Tipo de evento", payload.tipo_evento],
    ["WhatsApp", payload.whatsapp],
    ["Comuna", payload.comuna],
    ["Tipo de servicio", payload.tipo_servicio],
    ["Experiencia de pizzas", payload.experiencia_pizzas],
    ["Personas", payload.personas],
    ["Pizzas sugeridas", payload.pizzas_sugeridas],
    ["Composición", payload.composicion],
    ["Precio estimado", payload.precio_estimado_texto],
    ["Comentarios", payload.comentarios || "Sin comentarios"]
  ];

  const tableRows = rows
    .map(([label, value]) => `
      <tr>
        <td style="padding:10px 12px;border-bottom:1px solid #2a2a2a;color:#a99784;font-size:13px;">${escapeHtml(label)}</td>
        <td style="padding:10px 12px;border-bottom:1px solid #2a2a2a;color:#f3ebdd;font-size:14px;font-weight:600;">${escapeHtml(value)}</td>
      </tr>
    `)
    .join("");

  return `
    <div style="margin:0;padding:28px;background:#070707;color:#f3ebdd;font-family:Arial,sans-serif;">
      <div style="max-width:640px;margin:0 auto;border:1px solid #2a2a2a;background:#101011;padding:28px;">
        <p style="margin:0 0 10px;color:#b32025;font-size:12px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;">Nueva reserva</p>
        <h1 style="margin:0 0 16px;color:#f3ebdd;font-family:Georgia,serif;font-size:34px;line-height:1;">Festín Nápoles</h1>
        <p style="margin:0 0 22px;color:#d9cbbb;font-size:15px;line-height:1.5;">Entró una nueva solicitud desde la landing. Revisa disponibilidad y responde al cliente.</p>
        <table style="width:100%;border-collapse:collapse;">${tableRows}</table>
      </div>
    </div>
  `;
}

async function readJsonBody(request) {
  const chunks = [];

  for await (const chunk of request) {
    chunks.push(chunk);
  }

  return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}");
}

function validatePayload(payload) {
  const required = ["nombre", "fecha_evento", "tipo_evento", "whatsapp", "comuna", "tipo_servicio", "experiencia_pizzas", "personas"];
  return required.filter((field) => !payload[field]);
}

module.exports = async function handler(request, response) {
  response.setHeader("Access-Control-Allow-Origin", "*");
  response.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  response.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (request.method === "OPTIONS") {
    response.statusCode = 204;
    response.end();
    return;
  }

  if (request.method !== "POST") {
    sendJson(response, 405, { ok: false, error: "Método no permitido." });
    return;
  }

  const resendApiKey = process.env.RESEND_API_KEY;
  const resendTo = process.env.RESEND_TO || "seba.festinnapoles@gmail.com";
  const resendFrom = process.env.RESEND_FROM || "Festín Nápoles <onboarding@resend.dev>";
  const supabaseKey = process.env.SUPABASE_ANON_KEY || DEFAULT_SUPABASE_ANON_KEY;

  if (!resendApiKey) {
    sendJson(response, 500, { ok: false, error: "Falta configurar RESEND_API_KEY." });
    return;
  }

  try {
    const payload = await readJsonBody(request);
    const missingFields = validatePayload(payload);

    if (missingFields.length) {
      sendJson(response, 400, { ok: false, error: "Faltan datos obligatorios.", missingFields });
      return;
    }

    const supabaseResponse = await fetch(SUPABASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "apikey": supabaseKey,
        "Authorization": `Bearer ${supabaseKey}`,
        "Prefer": "return=representation"
      },
      body: JSON.stringify(payload)
    });

    if (!supabaseResponse.ok) {
      throw new Error(await supabaseResponse.text());
    }

    const [reservation] = await supabaseResponse.json();
    const emailResponse = await fetch(RESEND_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${resendApiKey}`
      },
      body: JSON.stringify({
        from: resendFrom,
        to: resendTo,
        subject: `Nueva reserva web Festín Nápoles - ${payload.nombre}`,
        html: buildReservationEmail(payload)
      })
    });

    if (!emailResponse.ok) {
      throw new Error(await emailResponse.text());
    }

    sendJson(response, 200, { ok: true, reservation });
  } catch (error) {
    console.error("Error al procesar reserva:", error);
    sendJson(response, 500, { ok: false, error: "No se pudo procesar la reserva." });
  }
};


