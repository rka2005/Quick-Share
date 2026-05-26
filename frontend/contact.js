const contactForm = document.getElementById("contactForm");
const contactStatus = document.getElementById("contactStatus");

contactForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const submitButton = contactForm.querySelector("button");

    const formData = {
        name: document.getElementById("contactName").value.trim(),
        email: document.getElementById("contactEmail").value.trim(),
        message: document.getElementById("contactMessage").value.trim(),
    };

    if (!formData.name || !formData.email || !formData.message) {

        contactStatus.textContent = "Please fill all fields.";
        contactStatus.classList.remove("hidden");

        return;
    }

    try {

        submitButton.disabled = true;
        submitButton.textContent = "Sending...";

        contactStatus.classList.remove("hidden");
        contactStatus.textContent = "Sending message...";

        const response = await fetch("/api/contact", {

            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify(formData),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Something went wrong");
        }

        contactStatus.textContent = "✅ Message sent successfully!";

        contactForm.reset();

    } catch (error) {

        console.error(error);

        contactStatus.textContent =
            "❌ Failed to send message. Please try again.";

    } finally {

        submitButton.disabled = false;
        submitButton.textContent = "Send Message";
    }
});