// ===== Termynal JavaScript for Terminal Animations =====

document.addEventListener('DOMContentLoaded', function() {
    const termynals = document.querySelectorAll(".termynal");
    termynals.forEach(termynal => new Termynal(termynal));
});

// Initialize Termynal animations
function Termynal(container, options) {
    const init = () => {
        this.container = container;
        this.container.setAttribute('data-termynal', "true");
        this.lines = getLines();
        setTimeout(() => startAnimation(), 600);  // Wait a bit for visual continuity
    };

    const getLines = () => {
        return [...this.container.querySelectorAll("[data-ty]")].map(line => {
            return {
                type: line.getAttribute("data-ty"),
                value: line.textContent,   // Preserve white space
                node: line
            };
        });
    };

    const startAnimation = () => {
        const cursor = document.createElement("span");
        cursor.className = "ty-cursor";
        cursor.innerHTML = "&#9608;";
        this.container.appendChild(cursor);
        animateLine(this.lines[0]);
    };

    const animateLine = (line, index = 0) => {
        if (line.type == "input") {
            line.node.classList.add("type");
            line.node.innerHTML = "";
            line.node.setAttribute("type", line.type);
            const chars = Array.from(line.value);
            chars.forEach((char, i) => {
                setTimeout(() => line.node.innerHTML += char, 75 * i);
            });
                setTimeout(() => nextLine(index), 75 * (chars.length + 1));
        } else if (line.type == "progress") {
            line.node.innerHTML = "[Processing...]";
            setTimeout(() => nextLine(index), 2000);
        } else {
            line.node.classList.add("type");
            nextLine(index);
        }
    };

    const nextLine = index => {
        if (index + 1 < this.lines.length) {
            animateLine(this.lines[index + 1], index + 1);
        }
    };

    const kill = () => {
        this.lines.forEach(line => delete line.value);
        this.container.setAttribute('data-termynal', "false");
    };

    this.init = init;
    this.kill = kill;
    init();
}
