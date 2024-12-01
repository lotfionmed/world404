document.addEventListener('DOMContentLoaded', () => {
    console.log('Traps script loaded');
    const trapButtons = document.querySelectorAll('.trap-trigger');
    
    console.log(`Found ${trapButtons.length} trap buttons`);
    
    trapButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            console.log('Trap button clicked');
            try {
                console.log('Fetching trap data...');
                const response = await fetch('/scary_trap');
                const trapData = await response.json();
                
                console.log('Trap data received:', trapData);
                
                switch(trapData.type) {
                    case 'message':
                        alert(trapData.content);
                        break;
                    case 'sound':
                        const audio = new Audio(`/static/sounds/${trapData.content}`);
                        audio.play();
                        break;
                    case 'visual':
                        document.body.classList.add('trap-screen-red');
                        setTimeout(() => {
                            document.body.classList.remove('trap-screen-red');
                        }, 2000);
                        break;
                    case 'jumpscare':
                        const jumpscareDiv = document.createElement('div');
                        jumpscareDiv.style.position = 'fixed';
                        jumpscareDiv.style.top = '0';
                        jumpscareDiv.style.left = '0';
                        jumpscareDiv.style.width = '100%';
                        jumpscareDiv.style.height = '100%';
                        jumpscareDiv.style.backgroundColor = 'black';
                        jumpscareDiv.style.zIndex = '9999';
                        jumpscareDiv.innerHTML = `
                            <img src="/static/images/jumpscare.gif" 
                                 style="position: absolute; 
                                        top: 50%; 
                                        left: 50%; 
                                        transform: translate(-50%, -50%); 
                                        max-width: 100%; 
                                        max-height: 100%;">
                        `;
                        document.body.appendChild(jumpscareDiv);
                        
                        const jumpscareAudio = new Audio('/static/sounds/scream.mp3');
                        jumpscareAudio.play();
                        
                        setTimeout(() => {
                            document.body.removeChild(jumpscareDiv);
                        }, 3000);
                        break;
                    case 'cursor-chaos':
                        document.body.style.cursor = 'none';
                        const cursorChaosDiv = document.createElement('div');
                        cursorChaosDiv.style.position = 'fixed';
                        cursorChaosDiv.style.top = '0';
                        cursorChaosDiv.style.left = '0';
                        cursorChaosDiv.style.width = '100%';
                        cursorChaosDiv.style.height = '100%';
                        cursorChaosDiv.style.pointerEvents = 'none';
                        cursorChaosDiv.style.zIndex = '9998';
                        
                        document.addEventListener('mousemove', (event) => {
                            const ghost = document.createElement('div');
                            ghost.style.position = 'fixed';
                            ghost.style.left = `${event.clientX}px`;
                            ghost.style.top = `${event.clientY}px`;
                            ghost.style.width = '20px';
                            ghost.style.height = '20px';
                            ghost.style.backgroundColor = 'red';
                            ghost.style.borderRadius = '50%';
                            ghost.style.opacity = '0.7';
                            cursorChaosDiv.appendChild(ghost);
                            
                            setTimeout(() => {
                                cursorChaosDiv.removeChild(ghost);
                            }, 1000);
                        });
                        
                        document.body.appendChild(cursorChaosDiv);
                        
                        setTimeout(() => {
                            document.body.removeChild(cursorChaosDiv);
                            document.body.style.cursor = 'default';
                        }, 5000);
                        break;
                    case 'mouse_swap':
                        const cursor = document.createElement('div');
                        cursor.style.position = 'fixed';
                        cursor.style.width = '50px';
                        cursor.style.height = '50px';
                        cursor.style.backgroundImage = 'url("/static/images/cursed_cursor.png")';
                        cursor.style.backgroundSize = 'cover';
                        cursor.style.pointerEvents = 'none';
                        cursor.style.zIndex = '9999';
                        document.body.appendChild(cursor);
                        
                        document.addEventListener('mousemove', (e) => {
                            cursor.style.left = `${e.clientX - 25}px`;
                            cursor.style.top = `${e.clientY - 25}px`;
                        });
                        
                        setTimeout(() => {
                            document.body.removeChild(cursor);
                        }, 5000);
                        break;
                    case 'screen_glitch':
                        const glitchOverlay = document.createElement('div');
                        glitchOverlay.style.position = 'fixed';
                        glitchOverlay.style.top = '0';
                        glitchOverlay.style.left = '0';
                        glitchOverlay.style.width = '100%';
                        glitchOverlay.style.height = '100%';
                        glitchOverlay.style.backgroundColor = 'transparent';
                        glitchOverlay.style.zIndex = '9998';
                        glitchOverlay.style.pointerEvents = 'none';
                        glitchOverlay.style.animation = 'glitch 0.5s infinite';
                        
                        const glitchStyle = document.createElement('style');
                        glitchStyle.textContent = `
                            @keyframes glitch {
                                0% { transform: translate(0); }
                                20% { transform: translate(-2px, 2px); }
                                40% { transform: translate(-2px, -2px); }
                                60% { transform: translate(2px, 2px); }
                                80% { transform: translate(2px, -2px); }
                                100% { transform: translate(0); }
                            }
                        `;
                        
                        document.head.appendChild(glitchStyle);
                        document.body.appendChild(glitchOverlay);
                        
                        setTimeout(() => {
                            document.body.removeChild(glitchOverlay);
                            document.head.removeChild(glitchStyle);
                        }, 3000);
                        break;
                    case 'fake_error':
                        const errorOverlay = document.createElement('div');
                        errorOverlay.style.position = 'fixed';
                        errorOverlay.style.top = '0';
                        errorOverlay.style.left = '0';
                        errorOverlay.style.width = '100%';
                        errorOverlay.style.height = '100%';
                        errorOverlay.style.backgroundColor = 'black';
                        errorOverlay.style.color = 'white';
                        errorOverlay.style.zIndex = '9999';
                        errorOverlay.style.display = 'flex';
                        errorOverlay.style.flexDirection = 'column';
                        errorOverlay.style.justifyContent = 'center';
                        errorOverlay.style.alignItems = 'center';
                        errorOverlay.style.fontFamily = 'monospace';
                        
                        errorOverlay.innerHTML = `
                            <h1>SYSTEM ERROR</h1>
                            <p>Critical failure detected. Initiating emergency shutdown...</p>
                            <p>Error Code: 0x${Math.random().toString(16).substr(2, 8)}</p>
                        `;
                        
                        document.body.appendChild(errorOverlay);
                        
                        setTimeout(() => {
                            document.body.removeChild(errorOverlay);
                        }, 3000);
                        break;
                }
            } catch (error) {
                console.error('Trap error:', error);
            }
        });
    });
});
