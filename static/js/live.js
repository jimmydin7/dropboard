const socket = io();
socket.emit('join', { post_id: postId });

const whiteboard = document.getElementById('whiteboard');
const ctx = whiteboard.getContext('2d');
let selectedColor = '#00ff88';
let lines = [];
let drawing = false;
let lastX = null, lastY = null;

function drawLine(x1, y1, x2, y2, color) {
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(x1 * whiteboard.width, y1 * whiteboard.height);
    ctx.lineTo(x2 * whiteboard.width, y2 * whiteboard.height);
    ctx.strokeStyle = color;
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.globalAlpha = 0.85;
    ctx.shadowColor = color + '88';
    ctx.shadowBlur = 4;
    ctx.stroke();
    ctx.globalAlpha = 1.0;
    ctx.restore();
}

function drawLines() {
    ctx.clearRect(0, 0, whiteboard.width, whiteboard.height);
    for (const l of lines) {
        drawLine(l.x1, l.y1, l.x2, l.y2, l.color);
    }
}

document.querySelectorAll('.cloud-color').forEach(btn => {
    btn.addEventListener('click', () => {
        selectedColor = btn.getAttribute('data-color');
        document.querySelectorAll('.cloud-color').forEach(b => b.classList.remove('ring-4', 'ring-white'));
        btn.classList.add('ring-4', 'ring-white');
    });
});
document.querySelector('.cloud-color').classList.add('ring-4', 'ring-white');

whiteboard.addEventListener('mousedown', e => {
    drawing = true;
    const rect = whiteboard.getBoundingClientRect();
    lastX = (e.clientX - rect.left) / rect.width;
    lastY = (e.clientY - rect.top) / rect.height;
});

whiteboard.addEventListener('mousemove', e => {
    if (!drawing) return;
    const rect = whiteboard.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    drawLine(lastX, lastY, x, y, selectedColor);
    socket.emit('draw_line', { post_id: postId, x1: lastX, y1: lastY, x2: x, y2: y, color: selectedColor });
    lastX = x;
    lastY = y;
});

whiteboard.addEventListener('mouseup', () => { drawing = false; });
whiteboard.addEventListener('mouseleave', () => { drawing = false; });

socket.on('draw_line', line => {
    lines.push(line);
    drawLine(line.x1, line.y1, line.x2, line.y2, line.color);
});

socket.on('init_lines', data => {
    lines = data.lines || [];
    drawLines();
});

window.addEventListener('resize', drawLines);

const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');

function getRandomColor() {
    const palette = [
        '#00ff88', '#4ecdc4', '#ffe66d', '#a8e6cf', '#ff8b94', '#00d4ff',
        '#ffb347', '#b19cd9', '#ff6961', '#77dd77', '#f49ac2', '#aec6cf'
    ];
    return palette[Math.floor(Math.random() * palette.length)];
}

let userColor = localStorage.getItem('chat_user_color');
if (!userColor) {
    userColor = getRandomColor();
    localStorage.setItem('chat_user_color', userColor);
}

function addMessage(msg) {
    const div = document.createElement('div');
    div.className = 'mb-2';
    div.innerHTML = `<span>${msg.text}</span> <span class='text-xs text-gray-400'>${msg.time ? new Date(msg.time).toLocaleTimeString() : ''}</span>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener('submit', e => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    socket.emit('chat_message', { post_id: postId, text, color: userColor });
    addMessage({ text, time: Date.now(), color: userColor });
    chatInput.value = '';
});

socket.on('chat_message', msg => {
    addMessage(msg);
});

socket.on('init_messages', data => {
    chatBox.innerHTML = '';
    (data.messages || []).forEach(addMessage);
});

const votedOption = localStorage.getItem(`poll_vote_${postId}`);
let hasVoted = votedOption !== null;

if (hasVoted) {
    disableAllPollOptions();
    highlightVotedOption(parseInt(votedOption));
}

document.querySelectorAll('.poll-option').forEach(option => {
    option.addEventListener('click', function() {
        if (hasVoted) return;
        
        const optionIndex = parseInt(this.getAttribute('data-index'));
        
        localStorage.setItem(`poll_vote_${postId}`, optionIndex.toString());
        hasVoted = true;
        disableAllPollOptions();
        highlightVotedOption(optionIndex);
        
        socket.emit('poll_vote', { post_id: postId, option_index: optionIndex });
    });
});

function disableAllPollOptions() {
    document.querySelectorAll('.poll-option').forEach(option => {
        option.style.opacity = '0.6';
        option.style.cursor = 'not-allowed';
        option.classList.add('voted');
        option.onclick = null;
    });
}

function highlightVotedOption(optionIndex) {
    const votedElement = document.querySelector(`[data-index="${optionIndex}"]`);
    if (votedElement) {
        votedElement.style.borderColor = '#00ff88';
        votedElement.style.backgroundColor = 'rgba(0, 255, 136, 0.1)';
        votedElement.innerHTML += '<div class="text-neon-green text-sm mt-2">✓ You voted for this</div>';
    }
}

socket.on('poll_update', data => {
    if (data.post_id === postId && data.poll) {
        updatePollDisplay(data.poll);
    }
});

function updatePollDisplay(poll) {
    const totalVotes = poll.options.reduce((sum, option) => sum + option.votes, 0);
    document.getElementById('total-votes').textContent = totalVotes;
    
    poll.options.forEach((option, index) => {
        const optionElement = document.querySelector(`[data-index="${index}"]`);
        if (optionElement) {
            const voteCount = optionElement.querySelector('.vote-count');
            const progressBar = optionElement.querySelector('.bg-neon-cyan');
            
            voteCount.textContent = `${option.votes} vote${option.votes !== 1 ? 's' : ''}`;
            
            const percentage = totalVotes > 0 ? (option.votes / totalVotes * 100) : 0;
            progressBar.style.width = `${percentage}%`;
        }
    });
} 