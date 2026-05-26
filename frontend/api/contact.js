import nodemailer from "nodemailer";

const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD,
  },
});

export default async function handler(req, res) {

  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({
      success: false,
      message: "Method not allowed",
    });
  }

  try {
    const { name, email, message } = req.body;

    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        message: "All fields are required",
      });
    }

    await transporter.sendMail({
      from: `"Quick Share Contact" <${process.env.GMAIL_USER}>`,
      to: process.env.GMAIL_USER,
      replyTo: email,
      subject: `Quick Share Contact from ${name}`,

      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin:auto;">
          <h2 style="color:#6d4bd4;">New Quick Share Contact</h2>

          <p><strong>Name:</strong> ${name}</p>
          <p><strong>Email:</strong> ${email}</p>

          <div style="
            background:#f5f5f5;
            padding:15px;
            border-radius:10px;
            margin-top:15px;
          ">
            ${message}
          </div>

          <hr style="margin-top:20px;" />

          <p style="font-size:12px;color:#777;">
            Sent from Quick Share Contact Form
          </p>
        </div>
      `,
    });

    return res.status(200).json({
      success: true,
      message: "Message sent successfully!",
    });

  } catch (error) {

    console.error(error);

    return res.status(500).json({
      success: false,
      message: "Failed to send message",
    });
  }
}