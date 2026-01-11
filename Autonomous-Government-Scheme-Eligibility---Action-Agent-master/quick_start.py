"""
Quick Start Script for Government Scheme Agent
Instantly falls back to demo mode if quota is exceeded
"""
import asyncio
from datetime import datetime

async def quick_start():
    """Quick start with immediate fallback"""
    print("🏛️  GOVERNMENT SCHEME ELIGIBILITY AGENT - QUICK START")
    print("=" * 55)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Try quick initialization
    try:
        from main import get_government_scheme_agent
        agent_system = get_government_scheme_agent()
        
        print("🤖 Testing API quota availability...")
        
        # Quick quota test first
        quota_available = await agent_system.quick_quota_test()
        
        if not quota_available:
            raise Exception("API quota exhausted")
        
        # If quota is available, do full initialization
        print("✅ API quota available, initializing full system...")
        success = await agent_system.initialize_system()
        
        if success:
            print("✅ System operational! Starting web interface...")
            # Start the web server
            import uvicorn
            from web_interface import app
            
            print()
            print("🚀 WEB INTERFACE STARTING...")
            print("🌐 URL: http://localhost:8000")
            print("📋 Demo: http://localhost:8000/demo") 
            print("📚 API Docs: http://localhost:8000/docs")
            print()
            print("⌨️  Press Ctrl+C to stop")
            
            await uvicorn_serve(app)
        else:
            raise Exception("Agent initialization failed - quota likely exceeded")
            
    except Exception as e:
        print(f"⚠️  API quota exhausted or connectivity issue: {str(e)[:100]}")
        print()
        print("🎭 SWITCHING TO DEMO MODE...")
        print("   This shows full system capabilities without consuming quota")
        print()
        
        # Import and run demo mode
        try:
            from demo_mode import demo_mode
            demo_mode()
        except ImportError:
            print("📺 SYSTEM OVERVIEW:")
            print("   • 5-Agent Architecture using Google ADK patterns")
            print("   • Google Gemini AI (gemini-2.5-flash)")
            print("   • Complete government scheme eligibility system")
            print("   • Ready for production when API quota available")
            print()
            print("💡 To see full demonstration: python demo_mode.py")

async def uvicorn_serve(app):
    """Serve with uvicorn"""
    import uvicorn
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(quick_start())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 For quota-free demo: python demo_mode.py")