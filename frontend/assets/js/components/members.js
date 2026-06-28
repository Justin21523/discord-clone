// frontend/assets/js/components/members.js
import { renderPresenceIndicator } from './presence.js';

export async function renderMembers(containerId) {
    const container = document.getElementById(containerId);

    // In a real implementation, we would fetch members from the API
    // For now, we'll use mock data
    const members = [
        { id: 1, name: 'User01', color: 'grey', status: 'online', activity: 'Playing a game' },
        { id: 2, name: 'Bot', color: '#5865f2', status: 'online', is_bot: true },
        { id: 3, name: 'OfflineUser', color: '#747f8d', status: 'offline' },
        { id: 4, name: 'IdleUser', color: '#faa61a', status: 'idle', activity: 'Watching YouTube' },
        { id: 5, name: 'DNDUser', color: '#f04747', status: 'dnd', activity: 'Do not disturb' }
    ];

    // Group members by status
    const onlineMembers = members.filter(m => m.status === 'online');
    const idleMembers = members.filter(m => m.status === 'idle');
    const dndMembers = members.filter(m => m.status === 'dnd');
    const offlineMembers = members.filter(m => m.status === 'offline');

    let html = '';

    if (onlineMembers.length > 0) {
        html += `
            <div class="member-category">
                Online — ${onlineMembers.length}
            </div>
            ${onlineMembers.map(member => `
                <div class="member-item" data-user-id="${member.id}">
                    <div class="member-avatar" style="background-color: ${member.color}; position: relative;">
                        ${renderPresenceIndicatorHTML(member.status, member.activity)}
                    </div>
                    <div class="member-name">${member.name}${member.is_bot ? ' <span class="bot-tag">BOT</span>' : ''}</div>
                </div>
            `).join('')}
        `;
    }

    if (idleMembers.length > 0) {
        html += `
            <div class="member-category">
                Idle — ${idleMembers.length}
            </div>
            ${idleMembers.map(member => `
                <div class="member-item" data-user-id="${member.id}">
                    <div class="member-avatar" style="background-color: ${member.color}; position: relative;">
                        ${renderPresenceIndicatorHTML(member.status, member.activity)}
                    </div>
                    <div class="member-name">${member.name}${member.is_bot ? ' <span class="bot-tag">BOT</span>' : ''}</div>
                </div>
            `).join('')}
        `;
    }

    if (dndMembers.length > 0) {
        html += `
            <div class="member-category">
                Do Not Disturb — ${dndMembers.length}
            </div>
            ${dndMembers.map(member => `
                <div class="member-item" data-user-id="${member.id}">
                    <div class="member-avatar" style="background-color: ${member.color}; position: relative;">
                        ${renderPresenceIndicatorHTML(member.status, member.activity)}
                    </div>
                    <div class="member-name">${member.name}${member.is_bot ? ' <span class="bot-tag">BOT</span>' : ''}</div>
                </div>
            `).join('')}
        `;
    }

    if (offlineMembers.length > 0) {
        html += `
            <div class="member-category">
                Offline — ${offlineMembers.length}
            </div>
            ${offlineMembers.map(member => `
                <div class="member-item" data-user-id="${member.id}">
                    <div class="member-avatar" style="background-color: ${member.color}; position: relative;">
                        ${renderPresenceIndicatorHTML(member.status, member.activity)}
                    </div>
                    <div class="member-name">${member.name}${member.is_bot ? ' <span class="bot-tag">BOT</span>' : ''}</div>
                </div>
            `).join('')}
        `;
    }

    container.innerHTML = html;

    // Initialize presence indicators
    import('./presence.js').then(module => {
        module.initPresenceIndicators();
    }).catch(err => {
        console.error('Error importing presence module:', err);
    });
}

// Helper function to render presence indicator HTML
function renderPresenceIndicatorHTML(status, activity = null) {
    const colors = {
        'online': '#43b581',
        'idle': '#faa61a',
        'dnd': '#f04747',
        'offline': '#747f8d'
    };

    const statusText = {
        'online': 'Online',
        'idle': 'Idle',
        'dnd': 'Do Not Disturb',
        'offline': 'Offline'
    };

    return `
        <div class="presence-indicator" style="
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: ${colors[status]};
            position: absolute;
            bottom: 0;
            right: 0;
            border: 2px solid var(--bg-secondary);
            z-index: 1;
        " title="${statusText[status]}${activity ? ` - ${activity}` : ''}"></div>
    `;
}