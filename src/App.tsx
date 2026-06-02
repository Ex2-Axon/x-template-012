import { useState, useEffect, useMemo } from 'react'

/* ── 10x Effect: Paper Texture Filter ── */
const PaperFilter = () => (
  <svg style={{ position: 'absolute', width: 0, height: 0 }}>
    <filter id="paper-texture">
      <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="5" result="noise" />
      <feDiffuseLighting in="noise" lightingColor="#fff" surfaceScale="2">
        <feDistantLight azimuth="45" elevation="60" />
      </feDiffuseLighting>
    </filter>
  </svg>
)

/* ── 10x Effect: Floating Paper Scraps ── */
function PaperScraps() {
  const scraps = useMemo(() => Array.from({ length: 12 }, (_, i) => ({
    id: i,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    rotate: `${Math.random() * 360}deg`,
    size: `${20 + Math.random() * 40}px`,
    delay: `${Math.random() * 5}s`,
    duration: `${10 + Math.random() * 20}s`,
    opacity: 0.1 + Math.random() * 0.2,
  })), [])

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {scraps.map((s) => (
        <div
          key={s.id}
          className="absolute bg-surface rounded-sm animate-sway"
          style={{
            left: s.left,
            top: s.top,
            width: s.size,
            height: s.size,
            transform: `rotate(${s.rotate})`,
            animationDelay: s.delay,
            animationDuration: s.duration,
            opacity: s.opacity,
            filter: 'url(#paper-texture)',
            boxShadow: 'var(--shadow-cut-sm)',
          }}
        />
      ))}
    </div>
  )
}

/* ── Custom Loader from context ── */
function CustomLoader() {
  return (
    <div className="flex flex-col items-center gap-4 py-8">
      <span className="loader-paper"></span>
      <style>{`
        .loader-paper {
          width: 48px;
          height: 48px;
          border: 3px dotted var(--color-primary);
          border-style: solid solid dotted dotted;
          border-radius: 50%;
          display: inline-block;
          position: relative;
          box-sizing: border-box;
          animation: rotation 2s linear infinite;
        }
        .loader-paper::after {
          content: "";
          box-sizing: border-box;
          position: absolute;
          left: 0; right: 0; top: 0; bottom: 0;
          margin: auto;
          border: 3px dotted var(--color-accent);
          border-style: solid solid dotted;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          animation: rotationBack 1s linear infinite;
          transform-origin: center center;
        }
        @keyframes rotation { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @keyframes rotationBack { 0% { transform: rotate(0deg); } 100% { transform: rotate(-360deg); } }
      `}</style>
    </div>
  )
}

function App() {
  const [count, setCount] = useState(0)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20,
      })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div className="min-h-screen bg-bg-paper text-text-main font-body selection:bg-primary/20">
      <PaperFilter />
      <PaperScraps />

      {/* ── Main Content ── */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 py-20 flex flex-col items-center text-center">
        
        {/* Hero Section */}
        <div 
          className="mb-12 animate-reveal"
          style={{ transform: `translate(${mousePos.x * -0.5}px, ${mousePos.y * -0.5}px)` }}
        >
          <div className="inline-block px-4 py-1 mb-6 bg-accent/10 text-accent font-heading font-bold tracking-widest text-xs rounded-full border border-accent/20">
            NEW COLLECTION
          </div>
          
          <h1 className="text-6xl md:text-8xl font-heading font-black mb-6 tracking-tighter text-primary relative">
            <span className="relative z-10">CRAFTED VISION</span>
            <span 
              className="absolute inset-0 text-surface -z-10 translate-x-1 translate-y-1 select-none"
              style={{ filter: 'url(#paper-texture)' }}
            >
              CRAFTED VISION
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-text-muted max-w-2xl mx-auto leading-relaxed font-light italic">
            "Explore a world of intricate layers and gentle textures."
          </p>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full mb-20">
          <div className="paper-layer p-8 rounded-2xl flex flex-col items-center gap-4 animate-reveal [animation-delay:200ms]">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center text-primary">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <h3 className="text-2xl font-heading font-bold">Tactile Design</h3>
            <p className="text-text-muted">Feel the digital grain and layered shadows as you interact with each element.</p>
          </div>

          <div className="paper-layer p-8 rounded-2xl flex flex-col items-center gap-4 animate-reveal [animation-delay:400ms]">
            <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center text-accent">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
            <h3 className="text-2xl font-heading font-bold">Gentle Palette</h3>
            <p className="text-text-muted">A soothing mix of sage green and terracotta, inspired by natural paper dyes.</p>
          </div>
        </div>

        {/* Interaction Section */}
        <section className="w-full py-16 px-8 bg-surface/50 rounded-3xl border border-black/5 relative overflow-hidden animate-reveal [animation-delay:600ms]">
          <div className="relative z-10">
            <h2 className="text-4xl font-heading font-black mb-8">Ready to Craft?</h2>
            
            <div className="flex flex-col items-center gap-6">
              <button 
                onClick={() => setCount(c => c + 1)}
                className="group relative px-10 py-4 bg-primary text-white font-heading font-bold rounded-xl transition-all hover:bg-primary/90 hover:scale-105 active:scale-95 shadow-cut-md hover:shadow-lift-lg"
              >
                <span className="relative z-10 flex items-center gap-3">
                  DISCOVER MORE
                  <span className="bg-white/20 px-2 py-0.5 rounded text-sm">{count}</span>
                </span>
                <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl" />
              </button>

              <CustomLoader />
            </div>
          </div>

          {/* Decorative background shapes */}
          <div className="absolute -top-20 -right-20 w-64 h-64 bg-accent/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-64 h-64 bg-primary/5 rounded-full blur-3xl" />
        </section>

        {/* Footer */}
        <footer className="mt-20 pt-10 border-t border-black/5 w-full flex flex-col md:flex-row justify-between items-center gap-6 text-sm text-text-muted font-heading">
          <div className="flex items-center gap-4">
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            SYSTEM v1.12.0 — READY
          </div>
          <div className="flex gap-8">
            <a href="#" className="hover:text-primary transition-colors">Documentation</a>
            <a href="#" className="hover:text-primary transition-colors">GitHub</a>
            <a href="#" className="hover:text-primary transition-colors">Discord</a>
          </div>
        </footer>
      </main>

      {/* 10x Effect: Corner Ornaments */}
      <div className="fixed top-0 left-0 w-32 h-32 border-t-4 border-l-4 border-primary/20 pointer-events-none z-20 m-4 rounded-tl-3xl" />
      <div className="fixed bottom-0 right-0 w-32 h-32 border-b-4 border-r-4 border-accent/20 pointer-events-none z-20 m-4 rounded-br-3xl" />
    </div>
  )
}

export default App
