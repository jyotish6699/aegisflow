export const SessionService = {

    async create(sessionData) {

        const response = await fetch(
            "http://localhost:8000/sessions",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(sessionData)
            }
        );

        if (!response.ok) {
            throw new Error("Failed to create session.");
        }

        return await response.json();

    }

};