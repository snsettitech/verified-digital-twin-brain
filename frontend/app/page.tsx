import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 font-sans text-slate-900">
      {/* Simple Header */}
      <nav className="flex items-center justify-between px-8 py-6 bg-white border-b shadow-sm">
        <div className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
          Verified Twin
        </div>
        <div className="flex gap-4">
          <Link href="/dashboard" className="text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors">
            Go to Dashboard
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center max-w-4xl mx-auto">
        <div className="inline-block px-4 py-1.5 mb-6 text-xs font-semibold tracking-wider text-blue-700 uppercase bg-blue-100 rounded-full">
          Grounded Answers Only
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl mb-6">
          Your Knowledge, <span className="text-blue-600">Verified.</span>
        </h1>
        <p className="text-xl text-slate-600 mb-10 leading-relaxed">
          Interact with a digital twin that only answers based on your documents. 
          Every answer comes with citations. No hallucinations, just facts.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full justify-center">
          <Link 
            href="/dashboard" 
            className="px-8 py-4 bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-blue-700 transition-all shadow-lg hover:shadow-xl active:scale-95 text-center"
          >
            Start Chatting
          </Link>
          <button 
            className="px-8 py-4 bg-white text-slate-900 border-2 border-slate-200 rounded-xl font-bold text-lg hover:border-blue-600 transition-all active:scale-95"
          >
            Learn How it Works
          </button>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 text-left">
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <h3 className="text-lg font-bold mb-2">Source Citations</h3>
            <p className="text-slate-500 text-sm leading-relaxed">Every answer highlights exactly which document it came from. Complete transparency.</p>
          </div>
          
          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            </div>
            <h3 className="text-lg font-bold mb-2">Confidence Scores</h3>
            <p className="text-slate-500 text-sm leading-relaxed">See a real-time confidence percentage for every response. Know when to trust.</p>
          </div>

          <div className="p-6 bg-white rounded-2xl shadow-sm border border-slate-100">
            <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center mb-4">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
            </div>
            <h3 className="text-lg font-bold mb-2">Human Escalation</h3>
            <p className="text-slate-500 text-sm leading-relaxed">If the brain is unsure, it flags an expert for review instead of guessing. Pure accuracy.</p>
          </div>
        </div>
      </main>

      <footer className="py-10 text-center text-slate-400 text-sm border-t mt-12 bg-white">
        © 2025 Verified Digital Twin Brain. All rights reserved.
      </footer>
    </div>
  );
}
