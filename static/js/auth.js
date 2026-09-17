/* ============================================================
   ENGINEERS DAY 2026
   STUDENT PORTAL INTERACTION ENGINE
============================================================ */


/* ============================================================
   ELEMENTS
============================================================ */

const character =
    document.getElementById("engineerCharacter");

const speechBubble =
    document.getElementById("speechBubble");

const speechText =
    document.getElementById("speechText");

const loginForm =
    document.getElementById("studentLoginForm");

const continueBtn =
    document.getElementById("continueBtn");


/* ============================================================
   SPEECH ENGINE
============================================================ */

let speechTimer = null;


function speakEngineerSir(
    message,
    expression = "normal",
    shouldSpeak = true
) {

    if (!speechText || !character) {
        return;
    }


    /* -----------------------------------------------
       UPDATE TEXT
    ------------------------------------------------ */

    speechText.textContent = message;


    /* -----------------------------------------------
       RESET EXPRESSIONS
    ------------------------------------------------ */

    character.classList.remove(
        "happy",
        "thinking",
        "excited"
    );


    if (expression !== "normal") {

        character.classList.add(
            expression
        );

    }


    /* -----------------------------------------------
       Bubble animation
    ------------------------------------------------ */

    speechBubble.classList.remove(
        "speech-pop"
    );


    void speechBubble.offsetWidth;


    speechBubble.classList.add(
        "speech-pop"
    );


    /* -----------------------------------------------
       BROWSER VOICE
    ------------------------------------------------ */

    if (
        shouldSpeak &&
        "speechSynthesis" in window
    ) {

        window.speechSynthesis.cancel();


        const voice =
            new SpeechSynthesisUtterance(
                message
            );


        voice.lang = "en-IN";

        voice.rate = 0.92;

        voice.pitch = 1.05;

        voice.volume = 0.9;


        window.speechSynthesis.speak(
            voice
        );

    }


    /* -----------------------------------------------
       Auto reset
    ------------------------------------------------ */

    clearTimeout(
        speechTimer
    );


    speechTimer = setTimeout(
        () => {

            character.classList.remove(
                "happy",
                "thinking",
                "excited"
            );

        },
        3500
    );

}


/* ============================================================
   INITIAL GREETING
============================================================ */

window.addEventListener(
    "load",
    () => {

        setTimeout(
            () => {

                speakEngineerSir(
                    "Welcome, Engineer Sir! Let's get you enrolled.",
                    "happy"
                );

            },
            900
        );

    }
);


/* ============================================================
   CURSOR FOLLOWING
============================================================ */

let mouseX = 0;
let mouseY = 0;

let targetX = 0;
let targetY = 0;


document.addEventListener(
    "mousemove",
    (event) => {

        mouseX =
            event.clientX /
            window.innerWidth;

        mouseY =
            event.clientY /
            window.innerHeight;


        targetX =
            (mouseX - 0.5) * 22;

        targetY =
            (mouseY - 0.5) * 12;

    }
);


function animateCharacter() {

    if (!character) {
        return;
    }


    const currentTransform =
        character.style.getPropertyValue(
            "--cursor-x"
        );


    character.style.setProperty(
        "--cursor-x",
        `${targetX}px`
    );


    character.style.setProperty(
        "--cursor-y",
        `${targetY}px`
    );


    character.style.transform =
        `translate(${targetX}px, ${targetY}px)`;


    requestAnimationFrame(
        animateCharacter
    );

}


animateCharacter();


/* ============================================================
   FIELD ELEMENTS
============================================================ */

const studentId =
    document.getElementById(
        "student_id"
    );

const nameInput =
    document.getElementById(
        "name"
    );

const phoneInput =
    document.getElementById(
        "phone"
    );

const emailInput =
    document.getElementById(
        "email"
    );


/* ============================================================
   FIELD SPEECH
============================================================ */

function setupField(
    element,
    focusMessage,
    successMessage
) {

    if (!element) {
        return;
    }


    element.addEventListener(
        "focus",
        () => {

            speakEngineerSir(
                focusMessage,
                "thinking"
            );

            const field =
                element.closest(
                    ".field"
                );


            if (field) {

                field.classList.add(
                    "active-field"
                );

            }

        }
    );


    element.addEventListener(
        "blur",
        () => {

            const field =
                element.closest(
                    ".field"
                );


            if (field) {

                field.classList.remove(
                    "active-field"
                );

            }

        }
    );


    element.addEventListener(
        "input",
        () => {

            const field =
                element.closest(
                    ".field"
                );


            if (
                element.value.trim().length > 1
            ) {

                if (field) {

                    field.classList.add(
                        "completed"
                    );

                }

            }
            else {

                if (field) {

                    field.classList.remove(
                        "completed"
                    );

                }

            }

        }
    );


    element.addEventListener(
        "change",
        () => {

            if (
                element.value.trim().length > 1
            ) {

                speakEngineerSir(
                    successMessage,
                    "happy"
                );

            }

        }
    );

}


/* ============================================================
   STUDENT ID
============================================================ */

setupField(
    studentId,

    "Engineer Sir, start with your Student ID.",

    "Excellent, Engineer Sir! Now enter your full name."
);


/* ============================================================
   NAME
============================================================ */

setupField(
    nameInput,

    "Engineer Sir, your full name please.",

    "Perfect, Engineer Sir! Now let's add your mobile number."
);


/* ============================================================
   PHONE
============================================================ */

setupField(
    phoneInput,

    "Engineer Sir, please enter your mobile number.",

    "Good job, Engineer Sir! Now enter your email address."
);


/* ============================================================
   EMAIL
============================================================ */

setupField(
    emailInput,

    "Engineer Sir, your email address please.",

    "Excellent, Engineer Sir! Now choose where you want your OTP."
);


/* ============================================================
   AUTO NEXT FIELD
============================================================ */

if (studentId) {

    studentId.addEventListener(
        "change",
        () => {

            if (
                studentId.value.trim()
            ) {

                setTimeout(
                    () => {

                        if (nameInput) {

                            nameInput.focus();

                        }

                    },
                    900
                );

            }

        }
    );

}


if (nameInput) {

    nameInput.addEventListener(
        "change",
        () => {

            if (
                nameInput.value.trim()
            ) {

                setTimeout(
                    () => {

                        if (phoneInput) {

                            phoneInput.focus();

                        }

                    },
                    900
                );

            }

        }
    );

}


if (phoneInput) {

    phoneInput.addEventListener(
        "change",
        () => {

            if (
                phoneInput.value.trim()
            ) {

                setTimeout(
                    () => {

                        if (emailInput) {

                            emailInput.focus();

                        }

                    },
                    900
                );

            }

        }
    );

}


if (emailInput) {

    emailInput.addEventListener(
        "change",
        () => {

            if (
                emailInput.value.trim()
            ) {

                setTimeout(
                    () => {

                        speakEngineerSir(
                            "Excellent, Engineer Sir! Now choose Email OTP or Mobile OTP.",
                            "happy"
                        );

                    },
                    800
                );

            }

        }
    );

}


/* ============================================================
   PHONE INPUT — NUMBERS ONLY
============================================================ */

if (phoneInput) {

    phoneInput.addEventListener(
        "input",
        () => {

            phoneInput.value =
                phoneInput.value.replace(
                    /\D/g,
                    ""
                ).slice(
                    0,
                    10
                );

        }
    );

}


/* ============================================================
   STUDENT ID — AUTO UPPERCASE
============================================================ */

if (studentId) {

    studentId.addEventListener(
        "input",
        () => {

            studentId.value =
                studentId.value.toUpperCase();

        }
    );

}


/* ============================================================
   OTP OPTION
============================================================ */

const otpOptions =
    document.querySelectorAll(
        'input[name="otp_method"]'
    );


otpOptions.forEach(
    (option) => {

        option.addEventListener(
            "change",
            () => {

                if (
                    option.value === "EMAIL"
                ) {

                    speakEngineerSir(
                        "Email OTP selected, Engineer Sir. Ready to verify!",
                        "happy"
                    );

                }
                else {

                    speakEngineerSir(
                        "Mobile OTP selected, Engineer Sir. Ready to verify!",
                        "happy"
                    );

                }

            }
        );

    }
);


/* ============================================================
   FORM SUBMIT
============================================================ */

if (loginForm) {

    loginForm.addEventListener(
        "submit",
        (event) => {

            /* -------------------------------------------
               HTML VALIDATION
            -------------------------------------------- */

            if (
                !loginForm.checkValidity()
            ) {

                return;

            }


            /* -------------------------------------------
               CHARACTER REACTION
            -------------------------------------------- */

            speakEngineerSir(
                "Excellent, Engineer Sir! Generating your secure OTP now.",
                "excited"
            );


            /* -------------------------------------------
               BUTTON STATE
            -------------------------------------------- */

            if (continueBtn) {

                continueBtn.disabled =
                    true;

                continueBtn.innerHTML =
                    `
                    <span>⚡</span>
                    <span>Generating Secure OTP...</span>
                    `;

            }

        }
    );

}


/* ============================================================
   CHARACTER HOVER
============================================================ */

if (character) {

    character.addEventListener(
        "mouseenter",
        () => {

            speakEngineerSir(
                "Engineer Sir! Don't forget to complete the form.",
                "happy"
            );

        }
    );

}


/* ============================================================
   CLICK CHARACTER
============================================================ */

if (character) {

    character.addEventListener(
        "click",
        () => {

            speakEngineerSir(
                "Come on, Engineer Sir! Let's finish your enrollment!",
                "excited"
            );

        }
    );

}


/* ============================================================
   LIVE CLOCK
============================================================ */

const clock =
    document.getElementById(
        "liveClock"
    );


function updateClock() {

    if (!clock) {
        return;
    }


    const now =
        new Date();


    const hours =
        String(
            now.getHours()
        ).padStart(
            2,
            "0"
        );


    const minutes =
        String(
            now.getMinutes()
        ).padStart(
            2,
            "0"
        );


    const seconds =
        String(
            now.getSeconds()
        ).padStart(
            2,
            "0"
        );


    clock.textContent =
        `${hours}:${minutes}:${seconds}`;

}


updateClock();


setInterval(
    updateClock,
    1000
);


/* ============================================================
   RANDOM ENGINEERING MICRO-MESSAGES
============================================================ */

const idleMessages = [

    "Engineer Sir, looking good!",

    "Take your time, Engineer Sir.",

    "Almost there, Engineer Sir!",

    "Engineers verify everything, Sir.",

    "One more step, Engineer Sir.",

    "Let's build something amazing, Engineer Sir."

];


let idleIndex = 0;


setInterval(
    () => {

        /*
         * Don't interrupt the user while typing.
         */

        const active =
            document.activeElement;


        const isInput =
            active &&
            (
                active.tagName === "INPUT"
            );


        if (!isInput) {

            idleIndex =
                (
                    idleIndex + 1
                )
                %
                idleMessages.length;


            speakEngineerSir(
                idleMessages[idleIndex],
                "normal"
            );

        }

    },
    15000
);