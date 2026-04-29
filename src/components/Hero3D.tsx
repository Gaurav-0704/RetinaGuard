import { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";

// Hero scene: a stylized 3D heroine surrounded by floating mini-dashboards.
//
// The figure is built from low-poly wireframe primitives so she reads as
// elegant + geometric rather than literal. Around her, small chart tiles
// (bar, line, scatter, donut, KPI) gently orbit on a tilted ring — each
// tile is a tiny live-looking visualization that re-paints a few times
// per second. Reads as: "an analyst at the centre of her data."

const ACCENT = new THREE.Color("#4f8cff");
const WARM   = new THREE.Color("#ffd166");
const HAIR   = new THREE.Color("#7aa2ff");

// ---------- The heroine ----------
function Heroine() {
  const root = useRef<THREE.Group>(null);
  const torso = useRef<THREE.Mesh>(null);
  const hair = useRef<THREE.Group>(null);

  useFrame(({ clock, pointer }, delta) => {
    if (!root.current) return;
    const t = clock.getElapsedTime();
    root.current.rotation.y += delta * 0.18 + pointer.x * 0.004;
    root.current.rotation.x = THREE.MathUtils.lerp(
      root.current.rotation.x,
      pointer.y * -0.08,
      0.04,
    );
    if (torso.current) {
      const breath = 1 + Math.sin(t * 1.2) * 0.012;
      torso.current.scale.set(breath, 1, breath);
    }
    if (hair.current) {
      hair.current.children.forEach((c, i) => {
        c.rotation.z = Math.sin(t * 0.9 + i * 0.4) * 0.06;
      });
    }
  });

  const wire = (color: THREE.Color | string, opacity = 0.85) => (
    <meshBasicMaterial color={color} wireframe transparent opacity={opacity} />
  );

  return (
    <group ref={root} position={[0, -1.6, 0]}>
      {/* Pedestal */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
        <ringGeometry args={[1.4, 1.55, 64]} />
        <meshBasicMaterial color={ACCENT} transparent opacity={0.55} side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]}>
        <ringGeometry args={[1.7, 1.78, 64]} />
        <meshBasicMaterial color={WARM} transparent opacity={0.18} side={THREE.DoubleSide} />
      </mesh>

      {/* Dress */}
      <mesh position={[0, 0.7, 0]}>
        <coneGeometry args={[1.05, 1.6, 24, 1, true]} />
        {wire(ACCENT, 0.65)}
      </mesh>
      <mesh position={[0, 0.7, 0]}>
        <coneGeometry args={[1.02, 1.55, 24, 1, true]} />
        <meshBasicMaterial color="#050a1a" side={THREE.DoubleSide} />
      </mesh>

      {/* Belt */}
      <mesh position={[0, 1.5, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.42, 0.04, 12, 32]} />
        <meshBasicMaterial color={WARM} transparent opacity={0.95} />
      </mesh>

      {/* Torso */}
      <mesh ref={torso} position={[0, 1.95, 0]}>
        <cylinderGeometry args={[0.42, 0.5, 0.95, 16, 1, true]} />
        {wire(ACCENT, 0.7)}
      </mesh>
      <mesh position={[0, 1.95, 0]}>
        <cylinderGeometry args={[0.4, 0.48, 0.93, 16, 1, true]} />
        <meshBasicMaterial color="#050a1a" side={THREE.DoubleSide} />
      </mesh>

      {/* Shoulders */}
      <mesh position={[-0.5, 2.35, 0]}>
        <sphereGeometry args={[0.13, 12, 12]} />
        {wire(ACCENT, 0.85)}
      </mesh>
      <mesh position={[0.5, 2.35, 0]}>
        <sphereGeometry args={[0.13, 12, 12]} />
        {wire(ACCENT, 0.85)}
      </mesh>

      {/* Arms */}
      <group position={[-0.5, 2.32, 0]} rotation={[0, 0, 0.18]}>
        <mesh position={[-0.1, -0.55, 0]}>
          <cylinderGeometry args={[0.07, 0.09, 1.1, 10]} />
          {wire(ACCENT, 0.7)}
        </mesh>
        <mesh position={[-0.16, -1.12, 0]}>
          <sphereGeometry args={[0.09, 12, 12]} />
          {wire(WARM, 0.9)}
        </mesh>
      </group>
      <group position={[0.5, 2.32, 0]} rotation={[0, 0, -0.18]}>
        <mesh position={[0.1, -0.55, 0]}>
          <cylinderGeometry args={[0.07, 0.09, 1.1, 10]} />
          {wire(ACCENT, 0.7)}
        </mesh>
        <mesh position={[0.16, -1.12, 0]}>
          <sphereGeometry args={[0.09, 12, 12]} />
          {wire(WARM, 0.9)}
        </mesh>
      </group>

      {/* Neck */}
      <mesh position={[0, 2.55, 0]}>
        <cylinderGeometry args={[0.11, 0.13, 0.18, 12]} />
        {wire(ACCENT, 0.8)}
      </mesh>

      {/* Head */}
      <mesh position={[0, 2.82, 0]}>
        <sphereGeometry args={[0.32, 20, 20]} />
        {wire(ACCENT, 0.75)}
      </mesh>
      <mesh position={[0, 2.82, 0]}>
        <sphereGeometry args={[0.305, 20, 20]} />
        <meshBasicMaterial color="#050a1a" />
      </mesh>

      {/* Hair */}
      <group ref={hair} position={[0, 2.92, 0]}>
        <mesh position={[0, 0.05, 0]}>
          <sphereGeometry args={[0.36, 18, 18, 0, Math.PI * 2, 0, Math.PI / 1.8]} />
          {wire(HAIR, 0.85)}
        </mesh>
        {[
          { x: -0.28, z: -0.05, rot: 0.05 },
          { x: -0.18, z: -0.18, rot: 0.0 },
          { x: 0,     z: -0.22, rot: 0.0 },
          { x: 0.18,  z: -0.18, rot: 0.0 },
          { x: 0.28,  z: -0.05, rot: -0.05 },
        ].map((s, i) => (
          <mesh
            key={i}
            position={[s.x, -0.45, s.z]}
            rotation={[Math.PI / 2.2, s.rot, 0]}
          >
            <cylinderGeometry args={[0.05, 0.07, 0.95, 8]} />
            <meshBasicMaterial color={HAIR} transparent opacity={0.85} />
          </mesh>
        ))}
        <mesh position={[0.16, -0.4, -0.12]} rotation={[Math.PI / 2.2, 0, 0]}>
          <cylinderGeometry args={[0.025, 0.035, 0.9, 8]} />
          <meshBasicMaterial color={WARM} transparent opacity={0.9} />
        </mesh>
      </group>
    </group>
  );
}

// ---------- Mini chart tiles ----------

type TileKind = "bar" | "line" | "scatter" | "donut" | "kpi" | "area";

type Tile = {
  kind: TileKind;
  title: string;
  seed: number;
};

const TILES: Tile[] = [
  { kind: "bar",     title: "Revenue by region",  seed: 0.0 },
  { kind: "line",    title: "Weekly conversions", seed: 0.7 },
  { kind: "scatter", title: "Cohort retention",   seed: 1.4 },
  { kind: "donut",   title: "Channel mix",        seed: 2.1 },
  { kind: "kpi",     title: "MoM growth",         seed: 2.8 },
  { kind: "area",    title: "Pipeline volume",    seed: 3.5 },
  { kind: "bar",     title: "Top SKUs",           seed: 4.2 },
  { kind: "line",    title: "Forecast vs actual", seed: 4.9 },
  { kind: "scatter", title: "Feature importance", seed: 5.6 },
  { kind: "donut",   title: "Stock segments",     seed: 6.3 },
];

function MiniChart({ tile, time }: { tile: Tile; time: number }) {
  const w = 130;
  const h = 70;
  const pad = 8;
  const t = time + tile.seed;

  const blue = "#4f8cff";
  const gold = "#ffd166";
  const blueSoft = "#8db0ff";
  const dim = "#8693b1";

  const rand = (i: number) => {
    const x = Math.sin(tile.seed * 9.7 + i * 12.9898) * 43758.5453;
    return x - Math.floor(x);
  };

  let body: JSX.Element;

  if (tile.kind === "bar") {
    const n = 7;
    const bars: JSX.Element[] = [];
    for (let i = 0; i < n; i++) {
      const base = 0.3 + rand(i) * 0.7;
      const wobble = (Math.sin(t * 1.2 + i) + 1) * 0.1;
      const v = THREE.MathUtils.clamp(base + wobble, 0.1, 1);
      const bw = (w - pad * 2) / n - 2;
      const bh = v * (h - pad * 2);
      bars.push(
        <rect
          key={i}
          x={pad + i * (bw + 2)}
          y={h - pad - bh}
          width={bw}
          height={bh}
          fill={i === n - 1 ? gold : blue}
          opacity={0.85}
          rx={1}
        />,
      );
    }
    body = <>{bars}</>;
  } else if (tile.kind === "line" || tile.kind === "area") {
    const n = 12;
    const pts: [number, number][] = [];
    for (let i = 0; i < n; i++) {
      const v = 0.3 + (Math.sin(t * 0.8 + i * 0.6 + tile.seed) + 1) * 0.25 + rand(i) * 0.15;
      const x = pad + (i / (n - 1)) * (w - pad * 2);
      const y = h - pad - v * (h - pad * 2);
      pts.push([x, y]);
    }
    const d = pts.map((p, i) => (i === 0 ? `M${p[0]},${p[1]}` : `L${p[0]},${p[1]}`)).join(" ");
    if (tile.kind === "area") {
      const area = `${d} L${pts[pts.length - 1][0]},${h - pad} L${pts[0][0]},${h - pad} Z`;
      body = (
        <>
          <path d={area} fill={blue} opacity={0.18} />
          <path d={d} fill="none" stroke={blue} strokeWidth={1.5} />
          <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r={2.5} fill={gold} />
        </>
      );
    } else {
      body = (
        <>
          <path d={d} fill="none" stroke={blue} strokeWidth={1.5} />
          <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r={2.5} fill={gold} />
        </>
      );
    }
  } else if (tile.kind === "scatter") {
    const dots: JSX.Element[] = [];
    for (let i = 0; i < 16; i++) {
      const x = pad + rand(i) * (w - pad * 2);
      const y = pad + rand(i + 100) * (h - pad * 2);
      const drift = Math.sin(t + i) * 1.2;
      const r = 1.5 + rand(i + 50) * 1.5;
      dots.push(
        <circle
          key={i}
          cx={x + drift}
          cy={y}
          r={r}
          fill={i % 4 === 0 ? gold : blue}
          opacity={0.7 + rand(i + 30) * 0.3}
        />,
      );
    }
    body = <>{dots}</>;
  } else if (tile.kind === "donut") {
    const cx = w / 2;
    const cy = h / 2 + 4;
    const r = 18;
    const slices = [0.45, 0.25, 0.20, 0.10];
    const colors = [blue, gold, blueSoft, dim];
    let acc = -Math.PI / 2 + Math.sin(t * 0.4) * 0.05;
    body = (
      <>
        {slices.map((s, i) => {
          const a0 = acc;
          const a1 = acc + s * Math.PI * 2;
          acc = a1;
          const x0 = cx + Math.cos(a0) * r;
          const y0 = cy + Math.sin(a0) * r;
          const x1 = cx + Math.cos(a1) * r;
          const y1 = cy + Math.sin(a1) * r;
          const large = s > 0.5 ? 1 : 0;
          return (
            <path
              key={i}
              d={`M${cx},${cy} L${x0},${y0} A${r},${r} 0 ${large} 1 ${x1},${y1} Z`}
              fill={colors[i]}
              opacity={0.85}
            />
          );
        })}
        <circle cx={cx} cy={cy} r={r * 0.55} fill="#050a1a" />
      </>
    );
  } else {
    const v = 12 + Math.floor((Math.sin(t * 0.6) + 1) * 8);
    body = (
      <>
        <text
          x={pad}
          y={h / 2 + 6}
          fill={gold}
          style={{ font: "700 22px Geist, sans-serif" }}
        >
          +{v}.{Math.floor(rand(0) * 9)}%
        </text>
        <path
          d={`M${pad},${h - pad} L${w * 0.3},${h * 0.55} L${w * 0.55},${h * 0.45} L${w - pad},${h * 0.25}`}
          fill="none"
          stroke={blue}
          strokeWidth={1.2}
          opacity={0.7}
        />
      </>
    );
  }

  return (
    <div className="dash-tile">
      <div className="dash-tile-title">{tile.title}</div>
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="60">
        {body}
      </svg>
    </div>
  );
}

// ---------- Orbiting dashboard halo ----------
function DashboardHalo() {
  const group = useRef<THREE.Group>(null);
  const dotRefs = useRef<(THREE.Mesh | null)[]>([]);

  // Tick state drives the SVG re-paints. We bump it ~6 times per second
  // from inside useFrame — enough for the "live data" feel without
  // hammering React.
  const [tick, setTick] = useState(0);
  const lastTickAt = useRef(0);
  const timeRef = useRef(0);

  const points = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    const n = TILES.length;
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      const radius = 3.4;
      const shell = i % 2 === 0 ? 1.0 : 1.18;
      const yLift = ((i % 4) - 1.5) * 0.45;
      pts.push(
        new THREE.Vector3(
          Math.cos(a) * radius * shell,
          1.4 + yLift,
          Math.sin(a) * radius * shell * 0.65,
        ),
      );
    }
    return pts;
  }, []);

  const edgesGeom = useMemo(() => {
    const positions = new Float32Array(points.length * 6);
    for (let i = 0; i < points.length; i++) {
      const a = points[i];
      const b = points[(i + 1) % points.length];
      positions[i * 6 + 0] = a.x;
      positions[i * 6 + 1] = a.y;
      positions[i * 6 + 2] = a.z;
      positions[i * 6 + 3] = b.x;
      positions[i * 6 + 4] = b.y;
      positions[i * 6 + 5] = b.z;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    return g;
  }, [points]);

  useFrame(({ clock, pointer }, delta) => {
    if (!group.current) return;
    const t = clock.getElapsedTime();
    timeRef.current = t;

    group.current.rotation.y += delta * 0.18 + pointer.x * 0.002;
    group.current.rotation.x = THREE.MathUtils.lerp(
      group.current.rotation.x,
      0.18 + pointer.y * -0.05,
      0.04,
    );

    points.forEach((p, i) => {
      const dot = dotRefs.current[i];
      if (dot) {
        const mat = dot.material as THREE.MeshBasicMaterial;
        mat.color.lerpColors(ACCENT, WARM, (Math.sin(t * 0.6 + i) + 1) * 0.2);
        dot.position.y = p.y + Math.sin(t * 0.9 + i * 0.7) * 0.08;
      }
    });

    if (t - lastTickAt.current > 0.16) {
      lastTickAt.current = t;
      setTick((n) => n + 1);
    }
  });

  void tick;

  return (
    <group ref={group}>
      <lineSegments geometry={edgesGeom}>
        <lineBasicMaterial color={ACCENT} transparent opacity={0.22} />
      </lineSegments>

      {points.map((p, i) => (
        <group key={i} position={p}>
          <mesh ref={(m) => { dotRefs.current[i] = m; }}>
            <sphereGeometry args={[0.07, 12, 12]} />
            <meshBasicMaterial color={ACCENT} transparent />
          </mesh>
          <Html
            center
            distanceFactor={9}
            style={{ pointerEvents: "none", userSelect: "none" }}
          >
            <MiniChart tile={TILES[i]} time={timeRef.current} />
          </Html>
        </group>
      ))}
    </group>
  );
}

// ---------- Ambient particle field ----------
function Starfield({ count = 260 }) {
  const ref = useRef<THREE.Points>(null);

  const geom = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 9 + Math.random() * 9;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    return g;
  }, [count]);

  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.015;
  });

  return (
    <points ref={ref} geometry={geom}>
      <pointsMaterial size={0.045} color="#a9c5ff" transparent opacity={0.55} sizeAttenuation />
    </points>
  );
}

export default function Hero3D() {
  // Respect prefers-reduced-motion: render a calm static composition.
  const [reducedMotion, setReducedMotion] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(mq.matches);
    const onChange = () => setReducedMotion(mq.matches);
    mq.addEventListener?.("change", onChange);
    return () => mq.removeEventListener?.("change", onChange);
  }, []);

  if (reducedMotion) return <StaticHero />;

  return (
    <Canvas
      className="globe-canvas"
      dpr={[1, 2]}
      camera={{ position: [0, 1.6, 8.0], fov: 52 }}
      gl={{ antialias: true, alpha: true }}
    >
      <color attach="background" args={["#050a1a"]} />
      <ambientLight intensity={0.5} />
      <pointLight position={[5, 5, 5]} color="#4f8cff" intensity={1.4} />
      <pointLight position={[-4, -2, -3]} color="#ffd166" intensity={0.6} />
      <Starfield />
      <Heroine />
      <DashboardHalo />
    </Canvas>
  );
}

function StaticHero() {
  return (
    <div className="globe-canvas static-hero" aria-hidden>
      <svg viewBox="0 0 600 600" width="100%" height="100%">
        <defs>
          <radialGradient id="bg" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stopColor="#1a2960" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#050a1a" stopOpacity="0" />
          </radialGradient>
        </defs>
        <rect x="0" y="0" width="600" height="600" fill="#050a1a" />
        <circle cx="300" cy="240" r="240" fill="url(#bg)" />
        <ellipse cx="300" cy="500" rx="120" ry="14" fill="none" stroke="#4f8cff" strokeWidth="1.5" opacity="0.6" />
        <ellipse cx="300" cy="510" rx="150" ry="18" fill="none" stroke="#ffd166" strokeWidth="1" opacity="0.25" />
        <path d="M220 500 L300 320 L380 500 Z" fill="none" stroke="#4f8cff" strokeWidth="1.5" opacity="0.7" />
        <ellipse cx="300" cy="320" rx="42" ry="6" fill="#ffd166" opacity="0.9" />
        <path d="M268 320 L290 230 L310 230 L332 320 Z" fill="none" stroke="#4f8cff" strokeWidth="1.5" opacity="0.7" />
        <line x1="280" y1="240" x2="240" y2="350" stroke="#4f8cff" strokeWidth="2" opacity="0.7" />
        <line x1="320" y1="240" x2="360" y2="350" stroke="#4f8cff" strokeWidth="2" opacity="0.7" />
        <circle cx="240" cy="350" r="6" fill="#ffd166" />
        <circle cx="360" cy="350" r="6" fill="#ffd166" />
        <circle cx="300" cy="200" r="32" fill="#050a1a" stroke="#4f8cff" strokeWidth="1.5" />
        <path d="M268 200 Q300 150 332 200 Q330 240 320 280 L280 280 Q270 240 268 200 Z" fill="#7aa2ff" opacity="0.55" />
      </svg>
    </div>
  );
}
