import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Html } from "@react-three/drei";
import * as THREE from "three";
import { techs } from "../data/techs";

// Full-screen 3D hero. A wireframe sphere with tech labels distributed
// evenly on its surface using a Fibonacci lattice. Spins slowly and drifts
// with the cursor. Labels on the back of the sphere fade out so the
// rotation actually reads as depth.

const RADIUS = 3;
const ACCENT = new THREE.Color("#00e5ff");
const WARM = new THREE.Color("#ffb84d");

// Spread N points evenly on a sphere. Looks better than random.
function fibonacciSphere(count: number, radius: number): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  const phi = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < count; i++) {
    const y = 1 - (i / (count - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const theta = phi * i;
    pts.push(
      new THREE.Vector3(Math.cos(theta) * r * radius, y * radius, Math.sin(theta) * r * radius)
    );
  }
  return pts;
}

function Globe() {
  const group = useRef<THREE.Group>(null);
  const points = useMemo(() => fibonacciSphere(techs.length, RADIUS), []);

  const labelRefs = useRef<(HTMLDivElement | null)[]>([]);
  const dotRefs = useRef<(THREE.Mesh | null)[]>([]);
  const worldPos = useMemo(() => new THREE.Vector3(), []);

  useFrame(({ clock, pointer, camera }, delta) => {
    if (!group.current) return;

    // Auto-rotate + small cursor drift.
    group.current.rotation.y += delta * 0.12 + pointer.x * 0.003;
    group.current.rotation.x = THREE.MathUtils.lerp(group.current.rotation.x, pointer.y * -0.25, 0.04);

    // Fade labels that are facing away from the camera.
    points.forEach((p, i) => {
      worldPos.copy(p).applyMatrix4(group.current!.matrixWorld);
      const camDir = worldPos.clone().sub(camera.position).normalize();
      const pointDir = worldPos.clone().normalize();
      const facing = pointDir.dot(camDir); // -1 = front, +1 = back
      const opacity = THREE.MathUtils.clamp(1 - (facing + 1) * 0.55, 0.05, 1);

      const label = labelRefs.current[i];
      if (label) label.style.opacity = String(opacity);

      const dot = dotRefs.current[i];
      if (dot) {
        const mat = dot.material as THREE.MeshBasicMaterial;
        mat.opacity = opacity;
        dot.scale.setScalar(0.8 + (1 - (facing + 1) * 0.5) * 0.5);
        // Subtle cyan/amber color pulse.
        const t = clock.getElapsedTime();
        mat.color.lerpColors(ACCENT, WARM, (Math.sin(t * 0.6 + i) + 1) * 0.15);
      }
    });
  });

  return (
    <group ref={group}>
      {/* Solid sphere slightly smaller than the wireframe — it hides the back-side dots/labels. */}
      <mesh>
        <sphereGeometry args={[RADIUS * 0.985, 48, 48]} />
        <meshBasicMaterial color="#05080f" />
      </mesh>

      {/* Main wireframe shell. */}
      <mesh>
        <icosahedronGeometry args={[RADIUS, 2]} />
        <meshBasicMaterial color={ACCENT} wireframe transparent opacity={0.22} />
      </mesh>

      {/* Second warm-tinted shell for depth. */}
      <mesh rotation={[0.3, 0.5, 0]}>
        <icosahedronGeometry args={[RADIUS * 1.01, 1]} />
        <meshBasicMaterial color={WARM} wireframe transparent opacity={0.08} />
      </mesh>

      {/* Tech labels + dots. */}
      {points.map((p, i) => (
        <group key={i} position={p}>
          <mesh ref={(m) => { dotRefs.current[i] = m; }}>
            <sphereGeometry args={[0.07, 16, 16]} />
            <meshBasicMaterial color={ACCENT} transparent />
          </mesh>
          <Html
            center
            distanceFactor={8}
            style={{
              pointerEvents: "none",
              userSelect: "none",
              whiteSpace: "nowrap",
              transform: "translate(0, -18px)",
            }}
          >
            <div
              ref={(el) => { labelRefs.current[i] = el; }}
              className="tech-label"
            >
              {techs[i]}
            </div>
          </Html>
        </group>
      ))}
    </group>
  );
}

// Ambient dots behind the globe — cheap way to add depth.
function Starfield({ count = 220 }) {
  const ref = useRef<THREE.Points>(null);

  const geom = useMemo(() => {
    const g = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 9 + Math.random() * 8;
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
    if (ref.current) ref.current.rotation.y += delta * 0.02;
  });

  return (
    <points ref={ref} geometry={geom}>
      <pointsMaterial size={0.04} color="#7be0ff" transparent opacity={0.6} sizeAttenuation />
    </points>
  );
}

export default function TechGlobe() {
  return (
    <Canvas
      className="globe-canvas"
      dpr={[1, 2]}
      camera={{ position: [0, 0, 9], fov: 50 }}
      gl={{ antialias: true, alpha: true }}
    >
      <color attach="background" args={["#05080f"]} />
      <ambientLight intensity={0.4} />
      <pointLight position={[6, 4, 5]} color="#00e5ff" intensity={1.2} />
      <pointLight position={[-5, -4, -2]} color="#ffb84d" intensity={0.5} />
      <Starfield />
      <Globe />
    </Canvas>
  );
}
