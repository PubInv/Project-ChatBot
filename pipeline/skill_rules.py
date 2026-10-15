"""Canonical skill taxonomy and README keyword rules.

This is configuration, not algorithmic code. Keeping it separate makes
`enrich.py` easier to read and gives future admins one obvious file for tuning
the approved skill list and keyword heuristics.
"""

CANONICAL_SKILLS_BY_MAJOR = {
    "Computer Science & Software": [
        "Programming", "Software Engineering", "Web Development",
        "JavaScript", "TypeScript", "C++", "Machine Learning",
        "Computer Vision", "API Design", "Data Structures", "Compiler Theory",
        "Computer Science", "Theoretical CS",
    ],
    "Design & UX": [
        "UX Design", "UI Design", "Graphic Art", "Industrial Design",
        "Product Design", "Human-centered Design",
    ],
    "Electrical & Embedded Systems": [
        "Electronics", "Microelectronics", "Arduino", "Raspberry Pi",
        "Electrical Engineering", "Firmware", "Power Electronics",
        "Sensor Design", "Embedded Systems",
    ],
    "Math, Physics & Theory": [
        "Math", "Physics", "Advanced Calculus", "Geometry",
        "Cryptography", "Theoretical CS", "Abstract Thinking",
    ],
    "Mechanical Engineering": [
        "Mechanical Engineering", "Mechanical Design", "Machining", "3D CAD",
        "Thermodynamics", "Fluid Dynamics", "Materials Science", "Motor Control",
        "Electromechanical Design",
    ],
    "Fabrication & Making": [
        "3D Printing", "3D Modeling", "Hardware Design", "Making",
        "Metalworking", "Soldering", "Magnetics", "Optics",
    ],
    "Biomedical & Health": [
        "Biology", "Chemistry", "Health / Medicine", "Medical Devices",
        "Microscopy", "Ophthalmology", "Pulmonology",
    ],
    "Research & Knowledge Work": [
        "Research", "Writing", "Internet Research", "OSINT",
    ],
    "General / Cross-Functional": [
        "AI", "Creativity", "System Thinking", "Experimental Design",
        "Technical Writing", "Communication", "Organization",
        "Project Management", "Accounting",
    ],
}
ALL_CANONICAL = {s for skills in CANONICAL_SKILLS_BY_MAJOR.values() for s in skills}


SKILL_KEYWORDS: dict[str, list[str]] = {
    "Programming": [
        "python", "script", "code", "software", "program", "algorithm",
        "library", "module", "flask", "django", "backend", "repo", "function",
        "class ", "import ", "install", "pip install", "npm", "compiler",
    ],
    "Software Engineering": [
        "software architecture", "api server", "backend server", "rest api",
        "microservice", "database", "sql", "nosql", "deployment", "docker",
        "continuous integration", "test suite", "unit test",
    ],
    "Web Development": [
        "html", "css", "javascript", "react", "vue", "angular", "node.js",
        "frontend", "webpage", "website", "web app", "http server",
        "web interface", "browser", "d3.js", "svelte",
    ],
    "JavaScript": [
        "javascript", "node.js", "npm", "typescript", "react", "vue",
        "webpack", "babel", "json api", "d3.js",
    ],
    "TypeScript": ["typescript", ".ts ", "tsconfig"],
    "C++": [
        "c++", "cpp", "arduino sketch", "avr-gcc", "g++", "#include",
        "std::", "cmake",
    ],
    "Machine Learning": [
        "machine learning", "neural network", "deep learning", "training data",
        "model inference", "tensorflow", "pytorch", "scikit", "dataset",
        "classification", "regression", "transformer", "llm", "ai model",
    ],
    "Computer Vision": [
        "image processing", "opencv", "camera image", "object detection",
        "image recognition", "pixel", "frame rate", "video stream",
        "visual detection", "colony counting", "image analysis",
    ],
    "API Design": [
        "rest api", "api endpoint", "openapi", "swagger", "graphql",
        "api design", "http endpoint", "api call",
    ],
    "Data Structures": [
        "data structure", "linked list", "binary tree", "hash map",
        "queue", "stack", "graph algorithm", "bfs", "dfs",
    ],
    "Compiler Theory": [
        "compiler design", "build a compiler", "write a compiler",
        "abstract syntax tree", "ast node", "bytecode", "lexer ",
        "tokenizer", "language grammar", "grammar rule", "language parser",
        "compiler construction", "compile-time",
    ],
    "Computer Science": [
        "computer science", "algorithm", "computational", "turing",
        "church", "formal language", "automata",
    ],
    "Theoretical CS": [
        "theoretical computer", "church's thesis", "turing machine",
        "formal proof", "proof theory", "lambda calculus", "type theory",
        "quantum computing", "computability",
    ],
    "UX Design": [
        "user experience", "ux design", "usability", "user interface design",
        "wireframe", "prototype ui", "user flow", "accessibility",
    ],
    "UI Design": [
        "user interface", "ui design", "gui", "widget", "layout design",
        "visual design", "interface design", "dashboard design",
    ],
    "Graphic Art": [
        "graphic design", "illustration", "visual art", "typography",
        "svg art", "color design", "infographic",
    ],
    "Industrial Design": [
        "industrial design", "product form", "ergonomic", "aesthetics",
        "form factor", "design language",
    ],
    "Product Design": [
        "product design", "prototype design", "product development",
        "design specification", "design review",
    ],
    "Human-centered Design": [
        "human-centered", "human factors", "user research", "co-design",
        "participatory design", "interview users", "user needs",
    ],
    "Electronics": [
        "circuit", "pcb", "schematic", "breadboard", "wiring", "voltage",
        "current", "resistor", "capacitor", "transistor", "diode",
        "oscilloscope", "multimeter", "soldering iron", "electronic",
    ],
    "Microelectronics": [
        "microcontroller", "mcu", "stm32", "avr", "atmega328",
        "integrated circuit", "ic chip", "fpga", "asic",
        "microelectronic", "chip design",
    ],
    "Arduino": [
        "arduino", "esp8266", "esp32", "atmega328", "arduino uno",
        "arduino nano", "arduino mega", "arduino sketch",
    ],
    "Raspberry Pi": [
        "raspberry pi", "raspbian", "raspi", "rpi", "gpio", "raspberry",
    ],
    "Electrical Engineering": [
        "electrical engineering", "power supply", "ac/dc", "rectifier",
        "transformer", "inductor", "impedance", "signal conditioning",
        "signal processing", "pwm", "adc", "dac",
    ],
    "Firmware": [
        "firmware", "rtos", "freertos", "embedded software", "bootloader",
        "flash memory", "interrupt handler", "hal layer", "bare metal",
    ],
    "Power Electronics": [
        "power electronics", "motor driver", "h-bridge", "mosfet driver",
        "buck converter", "boost converter", "pwm control", "battery management",
        "solar charge", "power regulator",
    ],
    "Sensor Design": [
        "sensor design", "sensor circuit", "sensor module", "transducer",
        "accelerometer", "gyroscope", "barometer", "temperature sensor",
        "humidity sensor", "sensor calibrat", "adc reading", "analog sensor",
        "impedance sensor", "sensor array", "sensor fusion",
    ],
    "Embedded Systems": [
        "embedded system", "real-time", "uart", "spi protocol", "i2c protocol",
        "serial communication", "microcontroller program", "peripheral",
        "interrupt", "watchdog", "memory map",
    ],
    "Math": [
        "mathematical", "algebra", "equation", "formula", "computation",
        "numerical method", "statistics", "probability", "calculus",
        "trigonometry", "matrix", "linear algebra",
    ],
    "Physics": [
        "physics", "force", "energy", "momentum", "thermodynamic",
        "electromagnetic", "optics", "acoustic", "wave propagation",
        "kinetic", "potential energy", "newton",
    ],
    "Advanced Calculus": [
        "calculus", "differential equation", "integral", "laplace",
        "fourier", "gradient", "partial derivative",
    ],
    "Geometry": [
        "geometry", "geometric", "polygon", "tessellation", "spatial",
        "3d geometry", "solid geometry", "euclidean", "coordinate",
    ],
    "Cryptography": [
        "cryptography", "encryption", "hash function", "blockchain",
        "public key", "private key", "zero-knowledge", "digital signature",
    ],
    "Abstract Thinking": [
        "abstract", "theoretical model", "formal model", "conceptual",
        "first principles", "thought experiment",
    ],
    "Mechanical Engineering": [
        "mechanical engineer", "mechanism", "bearing", "gear", "shaft",
        "linkage", "stress analysis", "torque", "load bearing",
        "mechanical design", "kinematics", "dynamics",
    ],
    "Mechanical Design": [
        "mechanical design", "cad model", "part design", "assembly design",
        "tolerance", "fit and finish", "design for manufacture",
    ],
    "Machining": [
        "machining", "cnc", "lathe", "mill", "drill press", "metal shop",
        "fabricat", "turning", "grinding", "cutting tool",
    ],
    "3D CAD": [
        "solidworks", "fusion 360", "freecad", "openscad", "catia",
        "onshape", "cad ", "3d cad", ".stl", ".step", "solid model",
    ],
    "Thermodynamics": [
        "thermodynamic", "heat transfer", "thermal", "temperature",
        "insulation", "heat exchang", "entropy", "enthalpy",
        "combustion", "heat engine", "carnot",
    ],
    "Fluid Dynamics": [
        "fluid dynamic", "flow rate", "pressure drop", "viscosity",
        "turbulence", "laminar", "pump design", "hydraulic",
        "pneumatic", "ferrofluid", "fluid mechanic",
    ],
    "Materials Science": [
        "material science", "material property", "alloy", "composite",
        "polymer", "ceramic", "tensile strength", "yield stress",
        "biochar", "pyrolysis material",
    ],
    "Motor Control": [
        "motor control", "stepper motor", "servo motor", "brushless",
        "bldc", "pid control", "motor driver", "rpm control",
        "encoder feedback", "motor torque",
    ],
    "Electromechanical Design": [
        "electromechanical", "actuator", "solenoid", "electromagnet",
        "linear actuator", "voice coil", "magnetic actuator",
    ],
    "3D Printing": [
        "3d print", "fdm", "resin print", "filament", "gcode",
        "slicer", "cura", "prusa", "ultimaker", "pla", "abs",
        "additive manufactur",
    ],
    "3D Modeling": [
        "3d model", "3d design", "blender", "mesh", "stl file",
        "model geometry", "parametric model",
    ],
    "Hardware Design": [
        "hardware design", "pcb design", "kicad", "eagle cad",
        "hardware prototype", "circuit board", "enclosure design",
        "hardware platform",
    ],
    "Making": [
        "making", "fabricat", "workshop", "woodwork", "metalwork",
        "hand tool", "power tool", "weld", "solder", "build prototype",
        "physical build",
    ],
    "Metalworking": [
        "metal fabricat", "weld", "steel", "aluminum", "machined part",
        "sheet metal", "casting", "forging",
    ],
    "Soldering": [
        "soldering", "solder joint", "reflow", "wave solder", "iron tip",
    ],
    "Magnetics": [
        "magnet", "ferrofluid", "magnetic field", "permanent magnet",
        "electromagnet", "magnetic bearing", "flux", "coil",
    ],
    "Optics": [
        "optics ", "optical", "lens design", "lens system", "photodiode",
        "laser ", "infrared sensor", "spectrometer", "optical sensor",
        "wavelength", "light detection", "photosensor", "collimator",
    ],
    "Biology": [
        "biological", "biology", "microorganism", "bacteria", "cell culture",
        "microbiology", "dna", "protein", "organism", "botany", "plant",
        "biochar", "pathogen", "colony",
    ],
    "Chemistry": [
        "chemistry", "chemical reaction", "chemical compound",
        "chemical solution", "reagent", "catalyst", "titration",
        "ph level", "pyrolysis", "combustion chemistry",
        "acid-base", "chemical analysis",
    ],
    "Health / Medicine": [
        "medical", "patient", "clinical", "hospital", "treatment",
        "disease", "health", "ventilator", "oxygen therapy", "respiratory",
        "vital sign", "diagnosis", "first aid", "healthcare",
    ],
    "Medical Devices": [
        "medical device", "fda", "iec 60601", "iso 13485", "biocompatible",
        "regulatory", "clinical trial", "ce mark", "510k",
        "point of care", "diagnostic device",
    ],
    "Microscopy": [
        "microscop", "microscope", "magnif", "slide", "specimen",
        "cell imaging", "petri dish", "colony count",
    ],
    "Ophthalmology": ["ophthalmolog", "retina", "eye care", "vision test", "cornea"],
    "Pulmonology": ["pulmonolog", "lung", "respiratory", "spirometer", "breathing"],
    "Research": [
        "research", "literature review", "study", "experiment",
        "hypothesis", "data collection", "analysis", "survey",
        "investigation",
    ],
    "Writing": [
        "documentation", "technical report", "paper", "article",
        "wiki", "write up", "specification document",
    ],
    "Internet Research": [
        "internet research", "web search", "online resource",
        "open data", "data mining",
    ],
    "OSINT": ["osint", "open source intelligence", "public record"],
    "AI": [
        "artificial intelligence", "ai ", "llm", "gpt", "language model",
        "chatbot", "generative", "intelligent system",
    ],
    "Creativity": [
        "creative", "novel approach", "innovative", "inventive",
        "brainstorm", "ideation", "original design",
    ],
    "System Thinking": [
        "system thinking", "system design", "holistic", "integration",
        "end-to-end", "full system", "system architecture",
    ],
    "Experimental Design": [
        "experiment", "test rig", "prototype test", "validation",
        "measurement setup", "calibration", "bench test", "trial",
    ],
    "Technical Writing": [
        "technical writing", "user manual", "api documentation",
        "spec document", "datasheet", "changelog",
    ],
    "Communication": [
        "communication", "stakeholder", "coordinate", "collaborate",
        "present", "report to",
    ],
    "Organization": [
        "project management", "organization", "coordinate team",
        "task management", "planning",
    ],
    "Project Management": [
        "project management", "milestone", "sprint", "agile",
        "roadmap", "deliverable", "timeline",
    ],
    "Accounting": [
        "accounting", "finance", "budget", "cost analysis",
        "financial model", "ledger", "bookkeeping",
    ],
}
