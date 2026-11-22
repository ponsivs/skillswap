/**
 * SkillSwap Interactive Skill Map Visualizer
 * Renders dynamic node network graph using HTML5 Canvas & Particle Physics
 * Categorizes nodes: Center Hub, Category Clusters, Teaching, Learning, and Completed Skills
 */

class SkillMap {
    constructor(canvasId, sidebarId) {
        this.canvas = document.getElementById(canvasId);
        this.sidebar = document.getElementById(sidebarId);
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.links = [];
        this.selectedNode = null;
        this.hoveredNode = null;
        this.isDragging = false;
        this.draggedNode = null;
        this.scale = 1;
        this.panX = 0;
        this.panY = 0;

        this.initCanvasSize();
        window.addEventListener('resize', () => this.initCanvasSize());
        this.setupEvents();
        this.fetchData();
    }

    initCanvasSize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
    }

    fetchData() {
        fetch('/skills/api/map-data')
            .then(res => res.json())
            .then(data => {
                this.buildGraph(data);
                this.animate();
            })
            .catch(err => {
                console.error("Failed to load skill map data:", err);
            });
    }

    buildGraph(data) {
        const rawNodes = data.nodes || [];
        const rawLinks = data.links || [];

        // Distribute nodes around center
        this.nodes = rawNodes.map((n, i) => {
            let x, y;
            if (n.type === 'center') {
                x = this.centerX;
                y = this.centerY;
            } else if (n.type === 'category') {
                const angle = (i * 2 * Math.PI) / 6;
                x = this.centerX + Math.cos(angle) * 160;
                y = this.centerY + Math.sin(angle) * 140;
            } else {
                const angle = Math.random() * 2 * Math.PI;
                const dist = 220 + Math.random() * 80;
                x = this.centerX + Math.cos(angle) * dist;
                y = this.centerY + Math.sin(angle) * dist;
            }

            return {
                ...n,
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                radius: n.radius || 18
            };
        });

        // Resolve link references
        const nodeMap = new Map(this.nodes.map(n => [n.id, n]));
        this.links = rawLinks.map(l => ({
            source: nodeMap.get(l.source),
            target: nodeMap.get(l.target),
            strength: l.strength || 0.5
        })).filter(l => l.source && l.target);

        // Auto select first skill node if available
        const firstSkill = this.nodes.find(n => n.type === 'skill');
        if (firstSkill) {
            this.selectNode(firstSkill);
        }
    }

    setupEvents() {
        this.canvas.addEventListener('mousedown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const clickedNode = this.getNodeAt(mouseX, mouseY);
            if (clickedNode) {
                this.draggedNode = clickedNode;
                this.isDragging = true;
                this.selectNode(clickedNode);
            } else {
                this.isDragging = true;
                this.lastPanX = mouseX;
                this.lastPanY = mouseY;
            }
        });

        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (this.draggedNode && this.isDragging) {
                this.draggedNode.x = mouseX;
                this.draggedNode.y = mouseY;
                this.draggedNode.vx = 0;
                this.draggedNode.vy = 0;
            } else {
                const node = this.getNodeAt(mouseX, mouseY);
                this.canvas.style.cursor = node ? 'pointer' : 'grab';
                this.hoveredNode = node;
            }
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
            this.draggedNode = null;
        });

        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            const node = this.getNodeAt(mouseX, mouseY);
            if (node) this.selectNode(node);
        });
    }

    getNodeAt(x, y) {
        for (let i = this.nodes.length - 1; i >= 0; i--) {
            const n = this.nodes[i];
            const dx = n.x - x;
            const dy = n.y - y;
            if (Math.sqrt(dx * dx + dy * dy) <= n.radius + 5) {
                return n;
            }
        }
        return null;
    }

    selectNode(node) {
        this.selectedNode = node;
        if (!this.sidebar) return;

        if (node.type === 'center') {
            this.sidebar.innerHTML = `
                <div class="d-flex align-items-center gap-2 mb-3">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: #4338CA;"></div>
                    <h5 class="mb-0 fw-bold">${node.label}</h5>
                </div>
                <p class="text-secondary small mb-3">Personal Learning Hub & Active Skills Network</p>
                <div class="p-3 rounded bg-dark border border-secondary mb-3">
                    <div class="d-flex justify-content-between small text-light mb-1">
                        <span>Total Skills Tracked:</span>
                        <span class="fw-bold">${this.nodes.filter(n => n.type === 'skill').length}</span>
                    </div>
                    <div class="d-flex justify-content-between small text-light">
                        <span>Categories:</span>
                        <span class="fw-bold">${this.nodes.filter(n => n.type === 'category').length}</span>
                    </div>
                </div>
                <p class="small text-muted mb-0">Click any connected skill node to inspect progress, proficiency, and learning details.</p>
            `;
        } else if (node.type === 'category') {
            this.sidebar.innerHTML = `
                <div class="d-flex align-items-center gap-2 mb-2">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background: #7C3AED;"></div>
                    <h5 class="mb-0 fw-bold">${node.label}</h5>
                </div>
                <span class="badge bg-purple text-light mb-3">Category Domain</span>
                <p class="small text-secondary mb-0">Explore individual peer-taught skills under this academic & practical discipline.</p>
            `;
        } else {
            // Skill node
            const progress = node.progress || 0;
            const isTeaching = node.skill_type === 'teach';
            const isCompleted = node.skill_type === 'completed' || progress >= 100;

            this.sidebar.innerHTML = `
                <div class="d-flex align-items-center justify-content-between mb-2">
                    <span class="badge rounded-pill" style="background: ${node.color}; color: #fff; font-size: 0.75rem;">
                        ${node.status_label}
                    </span>
                    <span class="badge bg-secondary">${node.proficiency || 'Beginner'}</span>
                </div>
                <h4 class="fw-bold text-white mb-1">${node.label}</h4>
                <div class="text-info small mb-3">${node.category}</div>
                
                <p class="small text-light mb-3">${node.description || 'Practical peer-to-peer exchange skill.'}</p>

                <div class="mb-3">
                    <div class="d-flex justify-content-between text-light small mb-1">
                        <span>Skill Mastery Progress</span>
                        <span class="fw-bold text-cyan" id="progressValDisplay">${progress}%</span>
                    </div>
                    <div class="progress" style="height: 8px; background: #1E293B;">
                        <div class="progress-bar" id="progressBarDisplay" style="width: ${progress}%; background: ${node.color};"></div>
                    </div>
                </div>

                ${!isTeaching ? `
                <div class="p-2 rounded bg-dark border border-secondary mb-3">
                    <label class="form-label text-light small mb-1">Update Progress (%):</label>
                    <div class="d-flex gap-2">
                        <input type="range" class="form-range" min="0" max="100" step="5" value="${progress}" id="progressSlider">
                    </div>
                </div>
                ` : `
                <div class="alert alert-success p-2 small mb-3" style="background: rgba(22, 163, 74, 0.2); border-color: #16A34A; color: #86EFAC;">
                    <i data-lucide="check-circle" class="me-1"></i> You are an active mentor for this skill.
                </div>
                `}

                <div class="d-grid gap-2">
                    <a href="/skills/explore?q=${encodeURIComponent(node.label)}" class="btn btn-sm btn-outline-info">
                        Find Peer Partners for this Skill
                    </a>
                </div>
            `;

            // Wire up slider if available
            const slider = document.getElementById('progressSlider');
            if (slider) {
                slider.addEventListener('change', (e) => {
                    const newVal = parseInt(e.target.value);
                    document.getElementById('progressValDisplay').innerText = `${newVal}%`;
                    document.getElementById('progressBarDisplay').style.width = `${newVal}%`;
                    node.progress = newVal;

                    // Send AJAX update
                    const userSkillId = node.id.replace('skill_', '');
                    fetch('/skills/api/update-progress', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                        },
                        body: JSON.stringify({
                            user_skill_id: userSkillId,
                            progress: newVal
                        })
                    }).catch(console.error);
                });
            }
        }
        if (window.lucide) window.lucide.createIcons();
    }

    animate() {
        this.updatePhysics();
        this.render();
        requestAnimationFrame(() => this.animate());
    }

    updatePhysics() {
        // Simple force layout relaxation
        for (let i = 0; i < this.nodes.length; i++) {
            const n1 = this.nodes[i];
            if (n1 === this.draggedNode) continue;

            // Weak gravity to center
            if (n1.type !== 'center') {
                n1.vx += (this.centerX - n1.x) * 0.0004;
                n1.vy += (this.centerY - n1.y) * 0.0004;
            }

            // Repulsion between nodes
            for (let j = i + 1; j < this.nodes.length; j++) {
                const n2 = this.nodes[j];
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const minDist = n1.radius + n2.radius + 35;

                if (dist < minDist) {
                    const force = (minDist - dist) / dist * 0.05;
                    n1.vx -= dx * force;
                    n1.vy -= dy * force;
                    n2.vx += dx * force;
                    n2.vy += dy * force;
                }
            }
        }

        // Link spring forces
        for (const link of this.links) {
            const dx = link.target.x - link.source.x;
            const dy = link.target.y - link.source.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const targetDist = link.source.type === 'center' ? 120 : 70;
            const force = (dist - targetDist) * 0.008 * link.strength;

            if (link.source !== this.draggedNode && link.source.type !== 'center') {
                link.source.vx += dx * force;
                link.source.vy += dy * force;
            }
            if (link.target !== this.draggedNode) {
                link.target.vx -= dx * force;
                link.target.vy -= dy * force;
            }
        }

        // Apply friction and position
        for (const n of this.nodes) {
            if (n === this.draggedNode || n.type === 'center') continue;
            n.vx *= 0.88;
            n.vy *= 0.88;
            n.x += n.vx;
            n.y += n.vy;

            // Bounds containment
            n.x = Math.max(n.radius + 10, Math.min(this.canvas.width - n.radius - 10, n.x));
            n.y = Math.max(n.radius + 10, Math.min(this.canvas.height - n.radius - 10, n.y));
        }
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw connections
        for (const link of this.links) {
            this.ctx.beginPath();
            this.ctx.moveTo(link.source.x, link.source.y);
            this.ctx.lineTo(link.target.x, link.target.y);
            this.ctx.strokeStyle = link.source.type === 'center' ? 'rgba(99, 102, 241, 0.35)' : 'rgba(148, 163, 184, 0.2)';
            this.ctx.lineWidth = link.source.type === 'center' ? 2 : 1.2;
            this.ctx.stroke();
        }

        // Draw nodes
        for (const n of this.nodes) {
            const isHovered = this.hoveredNode === n;
            const isSelected = this.selectedNode === n;

            // Glow ring for selected or hovered
            if (isSelected || isHovered) {
                this.ctx.beginPath();
                this.ctx.arc(n.x, n.y, n.radius + 7, 0, Math.PI * 2);
                this.ctx.fillStyle = isSelected ? 'rgba(34, 211, 238, 0.4)' : 'rgba(255, 255, 255, 0.2)';
                this.ctx.fill();
            }

            // Main node circle
            this.ctx.beginPath();
            this.ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = n.color || '#4338CA';
            this.ctx.fill();
            this.ctx.lineWidth = 2;
            this.ctx.strokeStyle = '#FFFFFF';
            this.ctx.stroke();

            // Node label text
            this.ctx.font = n.type === 'center' ? 'bold 12px Inter' : '11px Inter';
            this.ctx.fillStyle = '#FFFFFF';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(n.label, n.x, n.y + n.radius + 14);
        }
    }
}

window.SkillMap = SkillMap;
