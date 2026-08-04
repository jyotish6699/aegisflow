// =====================================================
// Timeline Service
// =====================================================

export const TimelineService = {

    async get(sessionId) {

        const response = await fetch(

            `http://localhost:8000/timeline/${sessionId}`

        );

        if (!response.ok) {

            throw new Error("Failed to load timeline.");

        }

        return await response.json();

    }

};