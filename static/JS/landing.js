(() => {
  "use strict";


  /* =========================================================
     CURSOR
     ========================================================= */

  const cursorDot =
    document.getElementById("cursor-dot");

  const cursorRing =
    document.getElementById("cursor-ring");

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;

  let ringX = mouseX;
  let ringY = mouseY;


  const supportsFinePointer =
    window.matchMedia &&
    window.matchMedia("(pointer: fine)").matches;


  if (supportsFinePointer) {

    window.addEventListener(
      "mousemove",
      (event) => {

        mouseX = event.clientX;
        mouseY = event.clientY;

        if (cursorDot) {
          cursorDot.style.left =
            `${mouseX}px`;

          cursorDot.style.top =
            `${mouseY}px`;

          cursorDot.style.opacity = "1";
        }

        if (cursorRing) {
          cursorRing.style.opacity = "1";
        }

      },
      { passive: true }
    );


    function animateCursor() {

      ringX +=
        (mouseX - ringX) * 0.14;

      ringY +=
        (mouseY - ringY) * 0.14;

      if (cursorRing) {

        cursorRing.style.left =
          `${ringX}px`;

        cursorRing.style.top =
          `${ringY}px`;
      }

      requestAnimationFrame(
        animateCursor
      );
    }

    animateCursor();


    /* Hover expansion */

    const interactiveElements =
      document.querySelectorAll(
        "a, button"
      );

    interactiveElements.forEach(
      (element) => {

        element.addEventListener(
          "mouseenter",
          () => {

            if (!cursorRing) return;

            cursorRing.style.width =
              "46px";

            cursorRing.style.height =
              "46px";

            cursorRing.style.margin =
              "-23px 0 0 -23px";

            cursorRing.style.borderColor =
              "rgba(251,219,175,0.9)";
          }
        );


        element.addEventListener(
          "mouseleave",
          () => {

            if (!cursorRing) return;

            cursorRing.style.width =
              "30px";

            cursorRing.style.height =
              "30px";

            cursorRing.style.margin =
              "-15px 0 0 -15px";

            cursorRing.style.borderColor =
              "rgba(251,219,175,0.5)";
          }
        );

      }
    );

  }


  /* =========================================================
     SPOTLIGHT REVEAL
     ========================================================= */

  const revealImage =
    document.getElementById(
      "reveal-img"
    );


  function updateSpotlight(
    clientX,
    clientY
  ) {

    if (!revealImage) return;

    const rect =
      revealImage.getBoundingClientRect();

    const x =
      clientX - rect.left;

    const y =
      clientY - rect.top;


    const width =
      window.innerWidth;


    let radius;


    if (width < 480) {

      radius = 110;

    } else if (width < 780) {

      radius = 155;

    } else {

      radius = 250;

    }


    const gradient =
      `radial-gradient(
        circle ${radius}px at ${x}px ${y}px,
        #fff 0%,
        #fff 40%,
        rgba(255,255,255,0.75) 60%,
        rgba(255,255,255,0.4) 75%,
        rgba(255,255,255,0.12) 88%,
        transparent 100%
      )`;


    revealImage.style.webkitMaskImage =
      gradient;

    revealImage.style.maskImage =
      gradient;
  }


  window.addEventListener(
    "mousemove",
    (event) => {

      updateSpotlight(
        event.clientX,
        event.clientY
      );

    },
    { passive: true }
  );


  window.addEventListener(
    "touchmove",
    (event) => {

      const touch =
        event.touches[0];

      if (!touch) return;

      updateSpotlight(
        touch.clientX,
        touch.clientY
      );

    },
    { passive: true }
  );


  /* =========================================================
     SOFT PARALLAX
     ========================================================= */

  const visual =
    document.querySelector(
      ".hero-visual"
    );


  if (
    visual &&
    supportsFinePointer
  ) {

    window.addEventListener(
      "mousemove",
      (event) => {

        const x =
          (event.clientX /
            window.innerWidth -
            0.5);

        const y =
          (event.clientY /
            window.innerHeight -
            0.5);


        visual.style.transform =
          `translate(
            ${x * 7}px,
            ${y * 5}px
          )`;

      },
      { passive: true }
    );

  }


  /* =========================================================
     ACCESS BUTTON MICRO INTERACTION
     ========================================================= */

  const accessButtons =
    document.querySelectorAll(
      ".access-btn"
    );


  accessButtons.forEach(
    (button) => {

      button.addEventListener(
        "mousemove",
        (event) => {

          const rect =
            button.getBoundingClientRect();

          const x =
            event.clientX -
            rect.left;

          const y =
            event.clientY -
            rect.top;


          button.style.setProperty(
            "--mx",
            `${x}px`
          );

          button.style.setProperty(
            "--my",
            `${y}px`
          );

        },
        { passive: true }
      );

    }
  );


  /* =========================================================
     IMAGE LOAD FALLBACK
     ========================================================= */

  const baseImage =
    document.querySelector(
      ".hero-base-img"
    );


  if (baseImage) {

    baseImage.addEventListener(
      "error",
      () => {

        baseImage.style.backgroundImage =
          "linear-gradient(135deg, #2a1107, #c45a18)";

      }
    );

  }


  /* =========================================================
     PAGE LOAD
     ========================================================= */

  window.addEventListener(
    "load",
    () => {

      document.body.classList.add(
        "page-loaded"
      );

    }
  );

})();