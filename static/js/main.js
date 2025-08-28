// Material Design 交互效果
document.addEventListener('DOMContentLoaded', function() {
    // 波纹效果
    function createRipple(event) {
        const button = event.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');

        const oldRipple = button.getElementsByClassName('ripple')[0];
        if (oldRipple) {
            oldRipple.remove();
        }

        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // 为按钮添加波纹效果
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });

    // 表单验证
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('error');
                    isValid = false;
                } else {
                    input.classList.remove('error');
                }
            });

            if (!isValid) {
                e.preventDefault();
                showMessage('请填写所有必填字段', 'error');
            }
        });
    });

    // 验证码刷新
    const captchaImages = document.querySelectorAll('.captcha-image');
    captchaImages.forEach(img => {
        img.addEventListener('click', function() {
            refreshCaptcha();
        });
    });

    // 密码可见性切换
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });
    });

    // 动画效果
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // 观察需要动画的元素
    const animateElements = document.querySelectorAll('.menu-item, .container');
    animateElements.forEach(el => {
        observer.observe(el);
    });

    // 消息显示函数
    function showMessage(message, type = 'info') {
        const existingMessage = document.querySelector('.message');
        if (existingMessage) {
            existingMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        messageDiv.textContent = message;

        const container = document.querySelector('.container');
        container.insertBefore(messageDiv, container.firstChild);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    // 验证码刷新函数
    function refreshCaptcha() {
        fetch('/auth/captcha')
            .then(response => response.json())
            .then(data => {
                const captchaImg = document.querySelector('.captcha-image');
                const captchaId = document.querySelector('input[name="captcha_id"]');

                if (captchaImg && captchaId) {
                    captchaImg.src = data.captcha_image;
                    captchaId.value = data.captcha_id;
                }
            })
            .catch(error => {
                console.error('Error refreshing captcha:', error);
                showMessage('验证码刷新失败', 'error');
            });
    }

    // 页面加载动画
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);

    // 检查URL参数中的消息
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    if (message) {
        showMessage(message, 'success');
    }
});

// 添加CSS动画类
const style = document.createElement('style');
style.textContent = `
.ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    transform: scale(0);
    animation: ripple 0.6s linear;
    pointer-events: none;
}

@keyframes ripple {
    to {
        transform: scale(4);
        opacity: 0;
    }
}

.animate-in {
    animation: fadeInUp 0.6s ease-out forwards;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.error {
    border-color: #b00020 !important;
    box-shadow: 0 0 0 3px rgba(176, 0, 32, 0.1) !important;
}

.message {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

body.loaded .container {
    animation: slideIn 0.6s ease-out;
}
`;
document.head.appendChild(style);
