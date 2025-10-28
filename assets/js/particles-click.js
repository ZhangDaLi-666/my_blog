// 等待文档加载完毕
document.addEventListener('DOMContentLoaded', (event) => {
    // 检查 tsParticles 是否已加载
    if (typeof tsParticles === 'undefined') {
        console.error('tsParticles not loaded');
        return;
    }

    // 启动 tsParticles
    tsParticles.load("tsparticles", {
        fpsLimit: 60,
        interactivity: {
            events: {
                onClick: {
                    enable: true,
                    mode: "push", // 关键：启用点击模式为 "push"
                },
                onHover: {
                    enable: true,
                    mode: "repulse", // 可选：鼠标悬停时排斥颗粒
                },
                resize: true,
            },
            modes: {
                push: {
                    quantity: 4, // 每次点击推送4个颗粒
                },
                repulse: {
                    distance: 150,
                    duration: 0.4,
                },
            },
        },
        particles: {
            color: {
                value: "#ffffff",
            },
            links: {
                color: "#ffffff",
                distance: 150,
                enable: true,
                opacity: 0.5,
                width: 1,
            },
            collisions: {
                enable: true,
            },
            move: {
                direction: "none",
                enable: true,
                outModes: {
                    default: "bounce",
                },
                random: false,
                speed: 2, // 颗粒移动速度
                straight: false,
            },
            number: {
                density: {
                    enable: true,
                    area: 800,
                },
                value: 80, // 初始颗粒数量
            },
            opacity: {
                value: 0.5,
            },
            shape: {
                type: "circle",
            },
            size: {
                value: { min: 1, max: 5 },
            },
        },
        detectRetina: true,
    });
});