import os, json
from pathlib import Path
import gradio as gr

DATA_FILE = Path(os.environ.get("DATA_FILE", "personaforge_data.json"))

def load():
    try:
        return json.loads(DATA_FILE.read_text())
    except Exception:
        return {"projects":[],"characters":[],"voices":[],"memories":[],"scripts":[]}

data = load()

def save():
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def names(key):
    return [x["name"] for x in data[key]]

def add_character(name, personality, backstory, goals, motivations, fears, relationships, values, speech, catchphrases, emotions):
    name = (name or "").strip()
    if not name: return "Enter a character name."
    data["characters"].append({"name":name,"personality":personality,"backstory":backstory,"goals":goals,"motivations":motivations,"fears":fears,"relationships":relationships,"values":values,"speech_style":speech,"catchphrases":catchphrases,"emotional_traits":emotions})
    save()
    return f"Character '{name}' created."

def add_voice(name, kind, accent, tone, speed, pitch, auth):
    name = (name or "").strip()
    if not name: return "Enter a voice name."
    if kind == "Uploaded / cloned voice" and auth != "I confirm I own this voice or have permission":
        return "Authorization is required for uploaded/cloned voices."
    data["voices"].append({"name":name,"type":kind,"accent":accent,"tone":tone,"speed":speed,"pitch":pitch,"authorization":auth})
    save()
    return f"Voice '{name}' saved. A verified voice provider is required for actual cloning/generation."

def assign(character, voice):
    for c in data["characters"]:
        if c["name"] == character:
            c["voice"] = voice; save(); return f"Assigned {voice} to {character}."
    return "Select a character."

def memory(character, text, importance):
    if not character or not text.strip(): return "Select a character and enter a memory."
    data["memories"].append({"character":character,"memory":text.strip(),"importance":importance}); save()
    return "Memory saved."

def project(name, desc):
    name=(name or "").strip()
    if not name: return "Enter a project name."
    data["projects"].append({"name":name,"description":desc}); save()
    return f"Project '{name}' created."

def gemini(prompt):
    key=os.environ.get("GEMINI_API_KEY","").strip()
    if not key: return "[Demo mode] Set GEMINI_API_KEY in Colab to enable Gemini."
    try:
        from google import genai
        client=genai.Client(api_key=key)
        r=client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return r.text or "No response generated."
    except Exception as e:
        return f"Gemini error: {e}"

def roleplay(character, scene, message, history):
    if not character: return history, "Select a character."
    c=next((x for x in data["characters"] if x["name"]==character),None)
    prompt=f"""You are {c['name']}, a fictional character in PersonaForge AI.
Personality: {c['personality']}
Backstory: {c['backstory']}
Goals: {c['goals']}
Motivations: {c['motivations']}
Fears: {c['fears']}
Relationships: {c['relationships']}
Values: {c['values']}
Speech style: {c['speech_style']}
Catchphrases: {c['catchphrases']}
Emotional traits: {c['emotional_traits']}
Scene: {scene}
User: {message}
Respond naturally while staying in character."""
    reply=gemini(prompt)
    history=history or []
    history += [{"role":"user","content":message},{"role":"assistant","content":reply}]
    return history, ""

def script(title, fmt, premise, chars, tone, length):
    return gemini(f"""Write a {length} {fmt} titled "{title}".
Characters: {chars}
Tone: {tone}
Premise: {premise}
Use scene headings, action and dialogue where appropriate.""") if premise.strip() else "Enter a premise."

def analyze(text):
    if not text.strip(): return "Paste a script first."
    speakers=[]
    for line in text.splitlines():
        s=line.strip()
        if s.endswith(":") and len(s)<80: speakers.append(s[:-1])
    return f"Lines: {len(text.splitlines())}\nDetected speakers: {', '.join(dict.fromkeys(speakers)) or 'None'}"

with gr.Blocks(title="PersonaForge AI") as app:
    gr.Markdown("# 🎭 PersonaForge AI\n### Create • Voice • Bring to Life")
    with gr.Tab("Characters"):
        n=gr.Textbox(label="Character Name"); p=gr.Textbox(label="Personality",lines=2); b=gr.Textbox(label="Backstory",lines=2)
        g=gr.Textbox(label="Goals"); m=gr.Textbox(label="Motivations"); f=gr.Textbox(label="Fears"); r=gr.Textbox(label="Relationships")
        v=gr.Textbox(label="Values"); s=gr.Textbox(label="Speech Style"); ca=gr.Textbox(label="Catchphrases"); e=gr.Textbox(label="Emotional Traits")
        cb=gr.Button("Create Character",variant="primary"); cs=gr.Textbox(label="Status")
        cb.click(add_character,[n,p,b,g,m,f,r,v,s,ca,e],cs)

    with gr.Tab("Voice Studio"):
        vn=gr.Textbox(label="Voice Name")
        vt=gr.Radio(["Original synthetic voice","Uploaded / cloned voice"],value="Original synthetic voice",label="Voice Type")
        ac=gr.Textbox(label="Accent"); to=gr.Textbox(label="Tone")
        sp=gr.Slider(.5,2,1,label="Speed"); pi=gr.Slider(-10,10,0,label="Pitch")
        au=gr.Dropdown(["Not applicable","I confirm I own this voice or have permission"],value="Not applicable",label="Authorization")
        vb=gr.Button("Save Voice Profile",variant="primary"); vs=gr.Textbox(label="Status")
        ach=gr.Dropdown(choices=names("characters"),label="Character"); avo=gr.Dropdown(choices=names("voices"),label="Voice")
        ab=gr.Button("Assign Voice"); ast=gr.Textbox(label="Assignment")
        vb.click(add_voice,[vn,vt,ac,to,sp,pi,au],vs)
        ab.click(assign,[ach,avo],ast)

    with gr.Tab("Roleplay"):
        rc=gr.Dropdown(choices=names("characters"),label="Character"); scene=gr.Textbox(label="Scene",lines=3); msg=gr.Textbox(label="Message")
        chat=gr.Chatbot(type="messages",height=420); send=gr.Button("Send",variant="primary"); rs=gr.Textbox(show_label=False)
        send.click(roleplay,[rc,scene,msg,chat],[chat,rs])

    with gr.Tab("Memories"):
        mc=gr.Dropdown(choices=names("characters"),label="Character"); mt=gr.Textbox(label="Memory",lines=3)
        imp=gr.Dropdown(["Low","Medium","High"],value="Medium",label="Importance"); mb=gr.Button("Save Memory",variant="primary"); ms=gr.Textbox(label="Status")
        mb.click(memory,[mc,mt,imp],ms)

    with gr.Tab("Script Studio"):
        title=gr.Textbox(label="Title"); fmt=gr.Dropdown(["Screenplay","Short Film","TV Episode","YouTube Script","Podcast","Audiobook","Advertisement","Game Dialogue","Monologue"],value="Screenplay",label="Format")
        premise=gr.Textbox(label="Premise",lines=4); chars=gr.Textbox(label="Characters"); tone=gr.Textbox(label="Tone")
        length=gr.Dropdown(["short","medium-length","long"],value="medium-length",label="Length")
        gb=gr.Button("Generate Script",variant="primary"); out=gr.Textbox(label="Generated Script",lines=18)
        gb.click(script,[title,fmt,premise,chars,tone,length],out)
        si=gr.Textbox(label="Paste Script",lines=8); an=gr.Button("Analyze"); ao=gr.Textbox(label="Analysis"); an.click(analyze,si,ao)

    with gr.Tab("Projects"):
        pn=gr.Textbox(label="Project Name"); pd=gr.Textbox(label="Description",lines=3); pb=gr.Button("Create Project",variant="primary"); ps=gr.Textbox(label="Status")
        pb.click(project,[pn,pd],ps)

if __name__=="__main__":
    app.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", "10000")), share=False, debug=False)
