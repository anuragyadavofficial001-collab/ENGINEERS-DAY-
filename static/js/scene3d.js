/* =========================================================
   ENGINEERS DAY 2026
   THREE.JS ENGINEERING WORLD
========================================================= */

(() => {

    const container =
        document.getElementById("threeScene");

    if (!container || typeof THREE === "undefined") {
        return;
    }


    /* =====================================================
       SCENE
    ====================================================== */

    const scene =
        new THREE.Scene();


    scene.background =
        new THREE.Color(0x08101f);


    scene.fog =
        new THREE.FogExp2(
            0x08101f,
            0.018
        );


    /* =====================================================
       CAMERA
    ====================================================== */

    const camera =
        new THREE.PerspectiveCamera(
            45,
            window.innerWidth /
            window.innerHeight,
            0.1,
            1000
        );


    camera.position.set(
        0,
        7,
        24
    );


    camera.lookAt(
        0,
        3,
        0
    );


    /* =====================================================
       RENDERER
    ====================================================== */

    const renderer =
        new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });


    renderer.setPixelRatio(
        Math.min(
            window.devicePixelRatio,
            2
        )
    );


    renderer.setSize(
        window.innerWidth,
        window.innerHeight
    );


    renderer.shadowMap.enabled = true;

    renderer.shadowMap.type =
        THREE.PCFSoftShadowMap;


    container.appendChild(
        renderer.domElement
    );


    /* =====================================================
       LIGHTING
    ====================================================== */

    const ambientLight =
        new THREE.AmbientLight(
            0x7899cc,
            1.5
        );

    scene.add(
        ambientLight
    );


    const sun =
        new THREE.DirectionalLight(
            0xffd6a0,
            3
        );


    sun.position.set(
        -12,
        18,
        10
    );


    sun.castShadow = true;

    scene.add(
        sun
    );


    const blueLight =
        new THREE.PointLight(
            0x168dff,
            7,
            35
        );


    blueLight.position.set(
        8,
        7,
        7
    );


    scene.add(
        blueLight
    );


    const greenLight =
        new THREE.PointLight(
            0x3aff9a,
            4,
            25
        );


    greenLight.position.set(
        -8,
        4,
        3
    );


    scene.add(
        greenLight
    );


    /* =====================================================
       MATERIALS
    ====================================================== */

    const groundMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x101b2d,
            roughness: .78,
            metalness: .18
        });


    const buildingMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x273852,
            roughness: .72
        });


    const steelMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x53677f,
            metalness: .75,
            roughness: .35
        });


    const glassMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x163b63,
            transparent: true,
            opacity: .55,
            metalness: .4,
            roughness: .15
        });


    const greenMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x2e9f61,
            roughness: .65
        });


    const darkGreenMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x185b3c,
            roughness: .7
        });


    const bellyMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x76c77d,
            roughness: .8
        });


    const helmetMaterial =
        new THREE.MeshStandardMaterial({
            color: 0xffb52e,
            roughness: .55
        });


    const blackMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x07101a,
            roughness: .35,
            metalness: .5
        });


    /* =====================================================
       GROUND
    ====================================================== */

    const ground =
        new THREE.Mesh(
            new THREE.PlaneGeometry(
                100,
                100
            ),
            groundMaterial
        );


    ground.rotation.x =
        -Math.PI / 2;


    ground.position.y =
        -1.2;


    ground.receiveShadow = true;

    scene.add(
        ground
    );


    /* =====================================================
       GRID
    ====================================================== */

    const grid =
        new THREE.GridHelper(
            100,
            50,
            0x1e6aa8,
            0x14263d
        );


    grid.position.y =
        -1.17;


    grid.material.transparent =
        true;


    grid.material.opacity =
        .25;


    scene.add(
        grid
    );


    /* =====================================================
       BUILDING CREATOR
    ====================================================== */

    function createBuilding(
        x,
        z,
        width,
        height,
        depth
    ) {

        const building =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    width,
                    height,
                    depth
                ),
                buildingMaterial
            );


        building.position.set(
            x,
            height / 2 - 1.2,
            z
        );


        building.castShadow = true;

        building.receiveShadow = true;

        scene.add(
            building
        );


        /* windows */

        const windowMaterial =
            new THREE.MeshStandardMaterial({
                color: 0x69caff,
                emissive: 0x155d91,
                emissiveIntensity: 1
            });


        for (
            let y = 1;
            y < height - 1;
            y += 1.7
        ) {

            for (
                let xx = -width / 2 + .8;
                xx < width / 2;
                xx += 1.5
            ) {

                const window =
                    new THREE.Mesh(
                        new THREE.BoxGeometry(
                            .55,
                            .65,
                            .04
                        ),
                        windowMaterial
                    );


                window.position.set(
                    x + xx,
                    y - 1.2,
                    z - depth / 2 - .03
                );


                scene.add(
                    window
                );

            }

        }

    }


    createBuilding(
        -13,
        -4,
        7,
        10,
        6
    );


    createBuilding(
        13,
        -5,
        8,
        13,
        7
    );


    createBuilding(
        17,
        -2,
        5,
        7,
        5
    );


    /* =====================================================
       CONSTRUCTION BUILDING
    ====================================================== */

    const unfinished =
        new THREE.Group();


    for (
        let floor = 0;
        floor < 4;
        floor++
    ) {

        const level =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    8,
                    .35,
                    5
                ),
                steelMaterial
            );


        level.position.set(
            8,
            floor * 2.1 + .5,
            -3
        );


        unfinished.add(
            level
        );


        for (
            let x = -3.5;
            x <= 3.5;
            x += 2.3
        ) {

            const pillar =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        .28,
                        2.1,
                        .28
                    ),
                    steelMaterial
                );


            pillar.position.set(
                8 + x,
                floor * 2.1 + 1.25,
                -3 - 2
            );


            unfinished.add(
                pillar
            );

        }

    }


    scene.add(
        unfinished
    );


    /* =====================================================
       CRANE
    ====================================================== */

    const crane =
        new THREE.Group();


    const craneVertical =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                .45,
                13,
                .45
            ),
            steelMaterial
        );


    craneVertical.position.y =
        5;


    craneVertical.position.x =
        13;


    craneVertical.position.z =
        -1;


    crane.add(
        craneVertical
    );


    const craneArm =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                11,
                .35,
                .35
            ),
            steelMaterial
        );


    craneArm.position.set(
        8,
        11,
        -1
    );


    crane.add(
        craneArm
    );


    const cable =
        new THREE.Mesh(
            new THREE.CylinderGeometry(
                .035,
                .035,
                5,
                8
            ),
            blackMaterial
        );


    cable.position.set(
        4,
        8.5,
        -1
    );


    crane.add(
        cable
    );


    const hook =
        new THREE.Mesh(
            new THREE.TorusGeometry(
                .3,
                .05,
                8,
                16,
                Math.PI
            ),
            helmetMaterial
        );


    hook.rotation.z =
        Math.PI;


    hook.position.set(
        4,
        6,
        -1
    );


    crane.add(
        hook
    );


    scene.add(
        crane
    );


    /* =====================================================
       CROCODILE ENGINEER
    ====================================================== */

    const crocodile =
        new THREE.Group();


    crocodile.position.set(
        0,
        1.5,
        3
    );


    scene.add(
        crocodile
    );


    /* BODY */

    const body =
        new THREE.Mesh(
            new THREE.SphereGeometry(
                2.0,
                12,
                8
            ),
            greenMaterial
        );


    body.scale.set(
        1.35,
        .8,
        1
    );


    body.castShadow = true;

    crocodile.add(
        body
    );


    /* BELLY */

    const belly =
        new THREE.Mesh(
            new THREE.SphereGeometry(
                1.55,
                12,
                8
            ),
            bellyMaterial
        );


    belly.scale.set(
        1.15,
        .62,
        .95
    );


    belly.position.set(
        0,
        -.15,
        1.05
    );


    crocodile.add(
        belly
    );


    /* HEAD */

    const head =
        new THREE.Mesh(
            new THREE.SphereGeometry(
                1.45,
                12,
                8
            ),
            greenMaterial
        );


    head.scale.set(
        1,
        .95,
        1.05
    );


    head.position.set(
        0,
        1.25,
        1.65
    );


    head.castShadow = true;

    crocodile.add(
        head
    );


    /* SNOUT */

    const snout =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                2.15,
                .72,
                1.45
            ),
            darkGreenMaterial
        );


    snout.position.set(
        0,
        1.05,
        2.55
    );


    snout.rotation.x =
        -.08;


    snout.castShadow = true;

    crocodile.add(
        snout
    );


    /* NOSE */

    const nose =
        new THREE.Mesh(
            new THREE.SphereGeometry(
                .22,
                8,
                8
            ),
            blackMaterial
        );


    nose.scale.z =
        .65;


    nose.position.set(
        0,
        1.17,
        3.3
    );


    crocodile.add(
        nose
    );


    /* EYES */

    function createEye(x) {

        const eye =
            new THREE.Mesh(
                new THREE.SphereGeometry(
                    .22,
                    10,
                    10
                ),
                new THREE.MeshStandardMaterial({
                    color: 0xf7f4cf,
                    emissive: 0x222000
                })
            );


        eye.position.set(
            x,
            1.85,
            2.05
        );


        crocodile.add(
            eye
        );


        const pupil =
            new THREE.Mesh(
                new THREE.SphereGeometry(
                    .1,
                    8,
                    8
                ),
                blackMaterial
            );


        pupil.position.set(
            x,
            1.85,
            2.22
        );


        crocodile.add(
            pupil
        );

    }


    createEye(-.52);

    createEye(.52);


    /* TEETH */

    const toothMaterial =
        new THREE.MeshStandardMaterial({
            color: 0xffffff,
            roughness: .4
        });


    for (
        let i = -4;
        i <= 4;
        i++
    ) {

        const tooth =
            new THREE.Mesh(
                new THREE.ConeGeometry(
                    .11,
                    .38,
                    6
                ),
                toothMaterial
            );


        tooth.position.set(
            i * .22,
            .72,
            3.22
        );


        tooth.rotation.x =
            Math.PI;


        crocodile.add(
            tooth
        );

    }


    /* HELMET */

    const helmet =
        new THREE.Group();


    const helmetTop =
        new THREE.Mesh(
            new THREE.SphereGeometry(
                .9,
                12,
                8,
                0,
                Math.PI * 2,
                0,
                Math.PI / 2
            ),
            helmetMaterial
        );


    helmetTop.scale.set(
        1.15,
        .65,
        1
    );


    helmet.add(
        helmetTop
    );


    const helmetBrim =
        new THREE.Mesh(
            new THREE.CylinderGeometry(
                1.05,
                1.05,
                .13,
                24
            ),
            helmetMaterial
        );


    helmetBrim.rotation.x =
        Math.PI / 2;


    helmetBrim.scale.z =
        .8;


    helmet.add(
        helmetBrim
    );


    helmet.position.set(
        0,
        2.5,
        1.7
    );


    crocodile.add(
        helmet
    );


    /* GOGGLES */

    const goggles =
        new THREE.Group();


    const lensMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x172f46,
            metalness: .5,
            roughness: .15
        });


    [-.48, .48].forEach(
        x => {

            const lens =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        .3,
                        .3,
                        .08,
                        16
                    ),
                    lensMaterial
                );


            lens.rotation.x =
                Math.PI / 2;


            lens.position.x =
                x;


            goggles.add(
                lens
            );

        }
    );


    const gogglesBar =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                .25,
                .09,
                .08
            ),
            blackMaterial
        );


    gogglesBar.position.x =
        0;


    goggles.add(
        gogglesBar
    );


    goggles.position.set(
        0,
        1.82,
        2.32
    );


    crocodile.add(
        goggles
    );


    /* =====================================================
       BACKPACK
    ====================================================== */

    const backpack =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                1.5,
                1.9,
                .65
            ),
            blackMaterial
        );


    backpack.position.set(
        0,
        .85,
        -.95
    );


    backpack.rotation.x =
        -.08;


    crocodile.add(
        backpack
    );


    /* backpack straps */

    const strapMaterial =
        new THREE.MeshStandardMaterial({
            color: 0x334459
        });


    [-.55, .55].forEach(
        x => {

            const strap =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        .13,
                        1.7,
                        .1
                    ),
                    strapMaterial
                );


            strap.position.set(
                x,
                1.0,
                .15
            );


            crocodile.add(
                strap
            );

        }
    );


    /* =====================================================
       BLUEPRINT
    ====================================================== */

    const blueprint =
        new THREE.Group();


    const paper =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                1.3,
                .08,
                2.0
            ),
            new THREE.MeshStandardMaterial({
                color: 0xc7dfff,
                roughness: .8
            })
        );


    blueprint.add(
        paper
    );


    const paperLineMaterial =
        new THREE.MeshBasicMaterial({
            color: 0x3474b7
        });


    for (
        let i = 0;
        i < 4;
        i++
    ) {

        const line =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    .8,
                    .015,
                    .025
                ),
                paperLineMaterial
            );


        line.position.set(
            0,
            .06,
            -.6 + i * .35
        );


        blueprint.add(
            line
        );

    }


    blueprint.position.set(
        1.45,
        .95,
        2.1
    );


    blueprint.rotation.x =
        -.3;


    blueprint.rotation.z =
        -.2;


    crocodile.add(
        blueprint
    );


    /* =====================================================
       CROCODILE LEGS
    ====================================================== */

    const legs = [];


    function createLeg(
        x,
        z
    ) {

        const legGroup =
            new THREE.Group();


        const upper =
            new THREE.Mesh(
                new THREE.CylinderGeometry(
                    .25,
                    .3,
                    1.1,
                    8
                ),
                greenMaterial
            );


        upper.rotation.z =
            x < 0
                ? -.25
                : .25;


        upper.position.y =
            -.9;


        legGroup.add(
            upper
        );


        const boot =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    .5,
                    .35,
                    .8
                ),
                blackMaterial
            );


        boot.position.set(
            x < 0 ? -.15 : .15,
            -1.48,
            .18
        );


        legGroup.add(
            boot
        );


        legGroup.position.set(
            x,
            .2,
            z
        );


        crocodile.add(
            legGroup
        );


        legs.push(
            legGroup
        );

    }


    createLeg(
        -.95,
        .6
    );


    createLeg(
        .95,
        .6
    );


    createLeg(
        -.9,
        -.6
    );


    createLeg(
        .9,
        -.6
    );


    /* =====================================================
       TAIL
    ====================================================== */

    const tail =
        new THREE.Group();


    for (
        let i = 0;
        i < 5;
        i++
    ) {

        const segment =
            new THREE.Mesh(
                new THREE.ConeGeometry(
                    .65 - i * .1,
                    1.2,
                    8
                ),
                greenMaterial
            );


        segment.rotation.z =
            Math.PI / 2;


        segment.position.x =
            -1.3 - i * .75;


        segment.position.y =
            .15 - i * .08;


        segment.scale.z =
            .8;


        tail.add(
            segment
        );

    }


    tail.position.z =
        -.2;


    crocodile.add(
        tail
    );


    /* =====================================================
       TOOL / RULER
    ====================================================== */

    const ruler =
        new THREE.Mesh(
            new THREE.BoxGeometry(
                .15,
                .15,
                2.3
            ),
            helmetMaterial
        );


    ruler.position.set(
        1.55,
        .4,
        1.4
    );


    ruler.rotation.x =
        -.4;


    ruler.rotation.z =
        -.3;


    crocodile.add(
        ruler
    );


    /* =====================================================
       FLOATING ENGINEERING PARTICLES
    ====================================================== */

    const particleGeometry =
        new THREE.BufferGeometry();


    const particleCount =
        900;


    const particlePositions =
        new Float32Array(
            particleCount * 3
        );


    for (
        let i = 0;
        i < particleCount;
        i++
    ) {

        particlePositions[i * 3] =
            (Math.random() - .5) * 60;

        particlePositions[i * 3 + 1] =
            Math.random() * 25 - 1;

        particlePositions[i * 3 + 2] =
            (Math.random() - .5) * 45;

    }


    particleGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(
            particlePositions,
            3
        )
    );


    const particleMaterial =
        new THREE.PointsMaterial({
            color: 0x7acbff,
            size: .035,
            transparent: true,
            opacity: .7
        });


    const particles =
        new THREE.Points(
            particleGeometry,
            particleMaterial
        );


    scene.add(
        particles
    );


    /* =====================================================
       MOUSE
    ====================================================== */

    let mouseX = 0;

    let mouseY = 0;

    let targetX = 0;

    let targetY = 0;


    window.addEventListener(
        "mousemove",
        event => {

            mouseX =
                (event.clientX /
                window.innerWidth) * 2 - 1;


            mouseY =
                (event.clientY /
                window.innerHeight) * 2 - 1;

        }
    );


    /* =====================================================
       CLOCK
    ====================================================== */

    const clock =
        new THREE.Clock();


    /* =====================================================
       ANIMATION
    ====================================================== */

    function animate() {

        requestAnimationFrame(
            animate
        );


        const elapsed =
            clock.getElapsedTime();


        targetX +=
            (mouseX - targetX) * .025;


        targetY +=
            (mouseY - targetY) * .025;


        /* camera */

        camera.position.x =
            targetX * 2.2;


        camera.position.y =
            7 - targetY * 1.2;


        camera.lookAt(
            0,
            3,
            1
        );


        /* crocodile */

        crocodile.rotation.y =
            Math.sin(elapsed * .45) * .12
            -
            targetX * .12;


        crocodile.position.y =
            1.5 +
            Math.sin(elapsed * 1.8) * .12;


        /* head movement */

        head.rotation.y =
            Math.sin(elapsed * 1.1) * .06;


        /* legs */

        legs.forEach(
            (leg, index) => {

                leg.rotation.z =
                    Math.sin(
                        elapsed * 3 +
                        index
                    ) * .08;

            }
        );


        /* tail */

        tail.rotation.y =
            Math.sin(
                elapsed * 1.5
            ) * .12;


        /* helmet */

        helmet.rotation.z =
            Math.sin(
                elapsed * .9
            ) * .025;


        /* crane */

        crane.rotation.y =
            Math.sin(
                elapsed * .18
            ) * .025;


        /* particles */

        particles.rotation.y =
            elapsed * .006;


        /* lights */

        blueLight.position.x =
            8 +
            Math.sin(elapsed * .7) * 2;


        greenLight.position.x =
            -8 +
            Math.cos(elapsed * .5) * 2;


        renderer.render(
            scene,
            camera
        );

    }


    animate();


    /* =====================================================
       RESIZE
    ====================================================== */

    window.addEventListener(
        "resize",
        () => {

            camera.aspect =
                window.innerWidth /
                window.innerHeight;


            camera.updateProjectionMatrix();


            renderer.setSize(
                window.innerWidth,
                window.innerHeight
            );

        }
    );


})();