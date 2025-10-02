document.addEventListener("DOMContentLoaded", () => {
    try {
        const tg = window.Telegram.WebApp;
        tg.ready();

        const loader = document.getElementById("loader");
        const petApp = document.getElementById("pet-app");
        const errorMessage = document.getElementById("error-message");

        const petNameEl = document.getElementById("pet-name");
        const petEmotionEl = document.getElementById("pet-emotion");
        const hungerBar = document.getElementById("hunger-bar");
        const hungerValue = document.getElementById("hunger-value");
        const thirstBar = document.getElementById("thirst-bar");
        const thirstValue = document.getElementById("thirst-value");
        const happinessBar = document.getElementById("happiness-bar");
        const happinessValue = document.getElementById("happiness-value");

        const feedButton = document.getElementById("feed-button");
        const waterButton = document.getElementById("water-button");
        const playButton = document.getElementById("play-button");

        const API_BASE_URL = "/api";

        function showError(message) {
            errorMessage.textContent = `🚫 Ошибка: ${message}`;
            errorMessage.classList.remove("hidden");
            petApp.classList.add("hidden");
            loader.classList.add("hidden");
        }

        function hideError() {
            errorMessage.classList.add("hidden");
        }

        function getEmotion(hunger, thirst, happiness) {
            const avg = (hunger + thirst + happiness) / 3;
            if (avg > 80) return "😃";
            if (avg > 60) return "🙂";
            if (avg > 40) return "😐";
            if (avg > 20) return "😟";
            return "😭";
        }

        function updateUI(pet) {
            if (!pet) return;
            petNameEl.textContent = pet.name;
            petEmotionEl.textContent = getEmotion(pet.hunger, pet.thirst, pet.happiness);
            hungerBar.style.width = `${pet.hunger}%`;
            hungerValue.textContent = `${pet.hunger}/100`;
            thirstBar.style.width = `${pet.thirst}%`;
            thirstValue.textContent = `${pet.thirst}/100`;
            happinessBar.style.width = `${pet.happiness}%`;
            happinessValue.textContent = `${pet.happiness}/100`;
        }

        async function fetchPetData() {
            try {
                loader.classList.remove("hidden");
                petApp.classList.add("hidden");
                hideError();

                const response = await fetch(`${API_BASE_URL}/pet`, {
                    headers: { "Authorization": `tma ${tg.initData}` }
                });

                if (response.status === 404) {
                    throw new Error("Питомец не найден. Создайте его в боте командой /pet.");
                }
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Ошибка сервера: ${errorText || response.statusText}`);
                }

                const pet = await response.json();
                updateUI(pet);
                loader.classList.add("hidden");
                petApp.classList.remove("hidden");
            } catch (error) {
                showError(error.message);
            }
        }

        async function handleInteraction(action) {
            hideError();
            setButtonsDisabled(true);
            try {
                const response = await fetch(`${API_BASE_URL}/pet/interact`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `tma ${tg.initData}`
                    },
                    body: JSON.stringify({ action })
                });

                if (!response.ok) {
                    const errorData = await response.text();
                    throw new Error(errorData || "Не удалось выполнить действие.");
                }

                const updatedPet = await response.json();
                updateUI(updatedPet);
                tg.HapticFeedback.notificationOccurred('success');
            } catch (error) {
                tg.showAlert(`Ошибка: ${error.message}`);
                tg.HapticFeedback.notificationOccurred('error');
            } finally {
                setButtonsDisabled(false);
            }
        }

        function setButtonsDisabled(disabled) {
            feedButton.disabled = disabled;
            waterButton.disabled = disabled;
            playButton.disabled = disabled;
        }

        feedButton.addEventListener("click", () => handleInteraction("feed"));
        waterButton.addEventListener("click", () => handleInteraction("water"));
        playButton.addEventListener("click", () => handleInteraction("play"));

        if (tg.initDataUnsafe && tg.initDataUnsafe.query_id) {
            fetchPetData();
        } else {
            showError("Не удалось получить данные для авторизации. Откройте приложение через Telegram.");
        }
    } catch (e) {
        const el = document.getElementById("error-message");
        el.textContent = `🚫 Критическая ошибка: ${e.message}`;
        el.classList.remove("hidden");
        document.getElementById("loader").classList.add("hidden");
        document.getElementById("pet-app").classList.add("hidden");
    }
});

window.onerror = function(message, source, lineno, colno, error) {
    const el = document.getElementById("error-message");
    if (el) {
        el.textContent = `🚫 Неперехваченная ошибка: ${message}`;
        el.classList.remove("hidden");
        document.getElementById("loader").classList.add("hidden");
        document.getElementById("pet-app").classList.add("hidden");
    }
    return true;
};