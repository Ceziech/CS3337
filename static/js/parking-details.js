document.addEventListener("DOMContentLoaded", function() {
    let statesData = [];
    const termsModal = new bootstrap.Modal(document.getElementById("termsModal"));
    termsModal.show();

    const agreeButton = document.getElementById("agreeButton");
    const cancelButton = document.getElementById("cancelButton");

    agreeButton.addEventListener("click", function () {
        termsModal.hide();
    });

    cancelButton.addEventListener("click", function () {
        const cancelUrl = cancelButton.getAttribute("data-url");
        if (cancelUrl) {
            window.location.href = cancelUrl;
        } else {
            console.error("Cancel URL not found.")
        }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const permit = urlParams.get("permit");
    const permitOptions = document.querySelectorAll(".permit-option");

    permitOptions.forEach(option => {
        const button = option.querySelector(".permit-button");
        const description = option.querySelector(".permit-description");

        if (permit === "event-parking" && (button.dataset.permit === "event" || button.dataset.permit === "athletic")) {
            option.style.display = "block";
            description.style.display = "block";
        } else if (permit === "visitor" && button.dataset.permit === "event") {
            option.style.display = "block";
            description.style.display = "block";
        } else if (permit === "nonaffiliated" && button.dataset.permit === "nonaffiliated") {
            option.style.display = "block";
            description.style.display = "block";
        } else if (permit === "highschool" && button.dataset.permit === "highschool") {
            option.style.display = "block";
            description.style.display = "block";
        } else if (permit === "2wheel" && button.dataset.permit === "2wheel") {
            option.style.display = "block";
            description.style.display = "block";
        } else {
            option.style.display = "none";
        }
    });

    const dateSelection = document.getElementById("dateSelection");
    const dateInput = document.getElementById("date-input");
    const calendarContainer = document.getElementById("calendar");
    const confirmDateBtn = document.getElementById("confirmDateBtn");

    const vehicleSelection = document.getElementById("vehicleSelection");
    const addVehicleBtn = document.getElementById("addVehicleBtn");

    let vehicleForm = null;

    async function fetchMakeModelData() {
        const response = await fetch('/static/MakeAndModels-Sheet1.csv');
        const data = await response.text();
        const rows = data.split('\n').map(row => row.split(','));
        const makeModelMap = {};

        rows.slice(1).forEach(row => {
            const make = row[0].trim();
            const model = row[1]?.trim();
            if (!makeModelMap[make]) {
                makeModelMap[make] = [];
            }
            if (model) {
                makeModelMap[make].push(model);
            }
        });

        return makeModelMap;
    }

    document.addEventListener("DOMContentLoaded", async function () {
        const makeModelMap = await fetchMakeModelData();
        const makeSelect = document.getElementById("vehicleMake");
        const modelSelect = document.getElementById("vehicleModel");

        Object.keys(makeModelMap).forEach(make => {
            const option = document.createElement("option");
            option.value = make;
            option.textContent = make;
            makeSelect.appendChild(option);
        });

        makeSelect.addEventListener("change", function () {
            const selectedMake = this.value;
            modelSelect.innerHTML = `<option value="">Select Model</option>`;
            if (makeModelMap[selectedMake]) {
                makeModelMap[selectedMake].forEach(model => {
                    const option = document.createElement("option");
                    option.value = model;
                    option.textContent = model;
                    modelSelect.appendChild(option);
                });
            }
        });
    });

    addVehicleBtn.addEventListener("click", function () {
        if (!vehicleForm) {
            vehicleForm = document.createElement("div");
            vehicleForm.className = "vehicle-form mt-3";
            vehicleForm.innerHTML = `
                <label for="plateNumber" class="form-label">Plate #*</label>
                <input type="text" id="plateNumber" class="form-control mb-2" placeholder="Enter Plate Number" maxlength="12" required>

                <label for="stateProv" class="form-label">State/Prov.*</label>
                <select id="stateProv" class="form-select mb-2" required>
                    <option value="">Select State/Province</option>
                </select>

                <label for="vehicleYear" class="form-label">Year*</label>
                <input type="number" id="vehicleYear" class="form-control mb-2" placeholder="Enter Vehicle Year" maxlength="4" required>

                <label for="vehicleMake" class="form-label">Make*</label>
                <select id="vehicleMake" class="form-select mb-2" required>
                    <option value="">Select Make</option>
                </select>

                <label for="vehicleModel" class="form-label">Model*</label>
                <select id="vehicleModel" class="form-select mb-2" required>
                    <option value="">Select Model</option>
                </select>

                <button id="saveVehicleBtn" class="btn btn-success mt-2">Save Vehicle</button>
                <button id="cancelVehicleBtn" class="btn btn-secondary mt-2 ms-2">Cancel</button>
            `;
            vehicleSelection.appendChild(vehicleForm);

            const stateDropdown = document.getElementById("stateProv");
            fetch("/static/states.json")
                .then(response => response.json())
                .then(states => {
                    statesData = states;
                    states.forEach(state => {
                        const option = document.createElement("option");
                        option.value = state.name;
                        option.textContent = state.name;
                        stateDropdown.appendChild(option);
                    });
                })
                .catch(error => console.error("Error loading States/Prov:", error));

            fetchMakeModelData().then(makeModelMap => {
                const makeSelect = document.getElementById("vehicleMake");
                const modelSelect = document.getElementById("vehicleModel");

                Object.keys(makeModelMap).forEach(make => {
                    const option = document.createElement("option");
                    option.value = make;
                    option.textContent = make;
                    makeSelect.appendChild(option);
                });

                makeSelect.addEventListener("change", function () {
                    const selectedMake = this.value;
                    modelSelect.innerHTML = `<option value="">Select Model</option>`;
                    if (makeModelMap[selectedMake]) {
                        makeModelMap[selectedMake].forEach(model => {
                            const option = document.createElement("option");
                            option.value = model;
                            option.textContent = model;
                            modelSelect.appendChild(option);
                        });
                    }
                });
            });

            const plateInput = document.getElementById("plateNumber");
            plateInput.addEventListener("input", function () {
                this.value = this.value.replace(/[^a-zA-Z0-9]/g, "").slice(0, 12).toUpperCase();
            });

            const yearInput = document.getElementById("vehicleYear");
            yearInput.addEventListener("input", function () {
                this.value = this.value.replace(/[^0-9]/g, "").slice(0, 4);
                const year = parseInt(this.value, 10);
                if (this.value.length === 4 && (year < 1900 || year > 2050)) {
                    this.value = "";
                }
            });

            document.getElementById("saveVehicleBtn").addEventListener("click", function () {
                const plate = plateInput.value.toUpperCase();
                const stateName = document.getElementById("stateProv").value;
                const year = yearInput.value;
                const make = document.getElementById("vehicleMake").value;
                const model = document.getElementById("vehicleModel").value;

                const stateData = statesData.find(state => state.name === stateName);
                const stateAbbreviation = stateData ? stateData.abbreviation : "";

                if (plate && stateName && year && make && model && stateAbbreviation) {
                    vehicleSelection.innerHTML = `
                        <h2 class="text-warning">Vehicle</h2>
                        <button class="confirmed-vehicle-btn" id="editVehicleBtn">
                            ${stateAbbreviation} ${plate.toUpperCase()} (${year} ${make} ${model}) &#10003;
                        </button>
                        <a href="${shopCartPageURL}" class="btn btn-danger mt-3">Add Permit to Cart</a>
                    `;

                    vehicleForm = null;
                    document.getElementById("editVehicleBtn").addEventListener("click", function () {
                        vehicleSelection.innerHTML = "";
                        addVehicleBtn.click();
                    });
                } else {
                    alert("Please fill out all fields to save your vehicle.");
                }
            });

            document.getElementById("cancelVehicleBtn").addEventListener("click", function () {
                vehicleForm.remove();
                vehicleForm = null;
            });

        }
    });

    dateInput.addEventListener("click", function () {
        calendarContainer.classList.toggle("hidden")
    });

    function initializeDatepicker() {
        const today = new Date();
        const maxDate = new Date(today);
        maxDate.setDate(today.getDate() + 20);

        $('#date-input').datepicker({
            format: 'mm/dd/yyyy',
            startDate: today,
            endDate: maxDate,
            todayHighlight: true,
            autoclose: true,
            orientation: 'bottom',
        });
    }

    function resetDateAndVehicleSelection() {
        vehicleSelection.style.display = "none";
        dateSelection.innerHTML = `
            <h2 class="text-warning">Date Selection</h2>
            <p>Please select a start date for this permit:</p>
            <div class="input-group date-picker-container">
                <input type="text" id="date-input" class="form-control" placeholder="Click to Select a Date" readonly>
            </div>
            <p>This permit will be valid for one day only</p>
            <button class="btn btn-warning mt-2 confirm-button" id="confirmDateBtn">Confirm</button>
        `;
        dateSelection.style.display = "block";

        initializeDatepicker();
        const newConfirmDateBtn = document.getElementById("confirmDateBtn");
        newConfirmDateBtn.addEventListener("click", function () {
            const dateInput = document.getElementById("date-input");
            if (dateInput.value) {
                dateSelection.innerHTML = `
                    <h2 class="text-warning">Dates</h2>
                    <div class="selected-date-box" id="selectedDate">${dateInput.value} - ${dateInput.value} &#10003;</div>
                    <button class="btn btn-warning btn-sm my-1 clickable" id="changeDate">Change Date</button>
                `;
                vehicleSelection.style.display = "block";

                const changeDate = document.getElementById("changeDate");
                changeDate.addEventListener("click", resetDateAndVehicleSelection);
            }
        });
    }

    permitOptions.forEach(option => {
        const button = option.querySelector(".permit-button");
        button.addEventListener("click", function () {
            const isSelected = button.classList.contains("selected-button");

            permitOptions.forEach(otherOption => {
                const otherButton = otherOption.querySelector(".permit-button");
                otherButton.classList.remove("selected-button");
                otherOption.querySelector("p").style.display = "block";

                if (permit === "event-parking" && (otherButton.dataset.permit === "event" || otherButton.dataset.permit === "athletic")) {
                    otherOption.style.display = "block";
                } else if (permit === "visitor" && otherButton.dataset.permit === "event") {
                    otherOption.style.display = "block";
                } else if (otherButton.dataset.permit === permit) {
                    otherOption.style.display = "block";
                } else {
                    otherOption.style.display = "none";
                }

                const checkmark = otherButton.querySelector(".checkmark");
                if (checkmark) {
                    checkmark.remove();
                }
            });

            loginButton.style.display = "block";

            if (!isSelected) {
                permitOptions.forEach(otherOption => {
                    if (otherOption !== option) {
                        otherOption.style.display = "none";
                    }
                });
                loginButton.style.display = "none";
                button.classList.add("selected-button");
                option.querySelector("p").style.display = "none";

                if (!button.querySelector(".checkmark")) {
                    const checkmark = document.createElement("span");
                    checkmark.classList.add("checkmark");
                    checkmark.innerHTML = "&#10003;";
                    button.appendChild(checkmark);
                }

                resetDateAndVehicleSelection();
            } else {
                dateSelection.style.display = "none";
                vehicleSelection.style.display = "none";

            }
        });
    });

    const loginButton = document.querySelector(".login-button");
    loginButton.addEventListener("click", function () {
        const loginUrl = loginButton.getAttribute("data-url");
        if (loginUrl) {
            window.location.href = loginUrl;
        } else {
            console.error("Login URL not found.");
        }
    });
});
