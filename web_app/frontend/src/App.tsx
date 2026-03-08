import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

// Get the API URL from environment variables, or default to localhost for development
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface HistoryItem {
  id: string;
  type: 'boot' | 'command' | 'output';
  command?: string;
  content: React.ReactNode;
}

const App: React.FC = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [input, setInput] = useState('');
  const [historyIdx, setHistoryIdx] = useState(-1);
  const [cmdList, setCmdList] = useState<string[]>([]);

  const [keyFile, setKeyFile] = useState<File | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initial boot sequence matching the exact design
    setHistory([
      {
        id: 'boot',
        type: 'boot',
        content: (
          <div className="mb-6">
            <p className="text-green font-bold">System boot complete.</p>
            <p className="text-dim mt-1">Welcome to CyberTerm OS v4.0.2</p>
            <p className="text-italic mt-1">AI-Enhanced Developer Environment</p>
            <p className="text-dim mt-4">Type <span className="text-cyan font-bold">"help"</span> to view a Quick Start Guide.</p>
          </div>
        )
      }
    ]);
  }, []);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [history]);

  const pushHistory = (item: Omit<HistoryItem, 'id'>) => {
    setHistory(prev => [...prev, { ...item, id: Math.random().toString(36).substring(2) }]);
  };

  const Prompt = () => (
    <span className="prompt whitespace-nowrap">
      <span className="text-cyan">guest@cyberterm:</span> <span className="text-main">~ $</span>
    </span>
  );

  const executeCommand = async (cmdStr: string) => {
    const args = cmdStr.trim().split(' ').filter(Boolean);
    const cmd = args[0]?.toLowerCase();

    pushHistory({ type: 'command', command: cmdStr, content: <Prompt /> });

    if (!cmd) return;

    let output: React.ReactNode = null;

    switch (cmd) {
      case 'help':
        output = (
          <div className="history-output text-dim font-inter">
            <p className="text-main font-bold mb-2">Available commands:</p>
            <p><span className="text-cyan font-mono font-bold">about</span> - Learn about the project</p>
            <p><span className="text-cyan font-mono font-bold">projects</span> - View portfolio</p>
            <p><span className="text-cyan font-mono font-bold">contact</span> - Connect with me</p>
            <p><span className="text-cyan font-mono font-bold">clear</span> - Clear terminal</p>
            <br />
            <p className="text-main font-bold mb-2">Security Tools (Quick Start Guide):</p>
            <p className="text-dim mb-1">1. Run <span className="text-cyan font-mono font-bold">generate mykey</span> to download a secure key file to your PC.</p>
            <p className="text-dim mb-1">2. Run <span className="text-cyan font-mono font-bold">load_key</span> to upload that generated .key file.</p>
            <p className="text-dim mb-1">3. Run <span className="text-cyan font-mono font-bold">encrypt [your secret message]</span> to scramble your text.</p>
            <p className="text-dim mb-1">4. Run <span className="text-cyan font-mono font-bold">decrypt [your scrambled text]</span> to reveal the original message.</p>
          </div>
        );
        break;
      case 'about':
        output = (
          <div className="history-output text-dim font-inter">
            <p>I am a senior UI/UX designer and frontend engineer.</p>
            <p>This is a custom terminal interface built to handle</p>
            <p>both immersive portfolio browsing and secure encryption.</p>
          </div>
        );
        break;
      case 'projects':
        output = (
          <div className="history-output font-inter">
            <p className="mb-2"><span className="text-green font-bold">✓</span> <span className="text-dim">Found 3 active deployments:</span></p>
            <p className="text-dim">- <span className="text-cyan underline cursor-pointer">NeuralSync-API</span> <span className="text-dim ml-1">(v1.2)</span></p>
            <p className="text-dim">- <span className="text-cyan underline cursor-pointer">Void-OS_Kernel</span> <span className="text-dim ml-1">(v0.9-beta)</span></p>
            <p className="text-dim">- <span className="text-cyan underline cursor-pointer">BIZIQ-Scrambler</span> <span className="text-dim ml-1">(v2.0)</span></p>
          </div>
        );
        break;
      case 'contact':
        output = (
          <div className="history-output font-inter text-dim">
            <p><span className="text-cyan font-bold">EMAIL</span>: nathan@cyberterm.os</p>
            <p><span className="text-cyan font-bold">LINKEDIN</span>: /in/nathanobochi</p>
          </div>
        );
        break;
      case 'clear':
        setHistory([]);
        return;
      case 'generate':
        const name = args[1] || 'mykey';
        try {
          const formData = new FormData();
          formData.append('name', name);
          const res = await axios.post(`${API_BASE}/generate-key`, formData, { responseType: 'blob' });
          const url = window.URL.createObjectURL(res.data);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${name}.key`;
          a.click();
          output = <div className="history-output font-inter"><span className="text-green font-bold">✓</span> <span className="text-dim">Key <span className="text-main font-mono">"{name}.key"</span> generated and downloaded.</span></div>;
        } catch (err: any) {
          output = <div className="history-output font-inter" style={{ color: '#ff5f56' }}>✖ Error generating key. Check API status.</div>;
        }
        break;

      case 'load_key':
        return new Promise<void>((resolve) => {
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = '.key';
          input.onchange = (e: any) => {
            const file = e.target.files?.[0];
            if (file) {
              setKeyFile(file);
              pushHistory({ type: 'output', content: <div className="history-output font-inter"><span className="text-green font-bold">✓</span> <span className="text-dim">Key <span className="text-main font-mono">"{file.name}"</span> loaded successfully.</span></div> });
            }
            resolve();
          };
          input.click();
          setTimeout(() => resolve(), 60000);
        });

      case 'encrypt':
      case 'decrypt':
        const textStr = args.slice(1).join(' ');
        if (!keyFile) {
          output = <div className="history-output font-inter text-dim" style={{ color: '#ff5f56' }}>✖ Error: No key loaded. Run '<span className="text-cyan">load_key</span>' first.</div>;
        } else if (!textStr) {
          output = <div className="history-output font-inter text-dim" style={{ color: '#ff5f56' }}>✖ Error: No text provided. Usage: {cmd} [text]</div>;
        } else {
          try {
            const formData = new FormData();
            formData.append('key_file', keyFile);

            if (cmd === 'encrypt') {
              formData.append('text', textStr);
            } else {
              formData.append('ciphertext', textStr);
            }

            const res = await axios.post(`${API_BASE}/${cmd}-text`, formData);
            const resultText = cmd === 'encrypt' ? res.data.ciphertext : res.data.plaintext;

            output = (
              <div className="history-output font-inter mt-1 mb-2">
                <p className="text-green font-bold mb-1">✓ {cmd.toUpperCase()}ION SUCCESSFUL:</p>

                <div className="mt-2 p-3 rounded" style={{ backgroundColor: 'rgba(255,255,255,0.03)', border: '1px solid rgba(0,210,255,0.2)' }}>
                  <p className="text-main font-mono mb-3" style={{ wordBreak: 'break-all', userSelect: 'text' }}>
                    {resultText}
                  </p>
                  <button
                    onClick={() => navigator.clipboard.writeText(resultText)}
                    className="text-cyan text-[11px] font-bold border border-cyan px-2 py-1 rounded hover:bg-cyan hover:text-[#0b1114] cursor-pointer transition-colors uppercase"
                  >
                    Copy {cmd === 'encrypt' ? 'Encrypted' : 'Decrypted'} Text
                  </button>
                </div>

                {cmd === 'encrypt' && (
                  <p className="text-dim text-[12px] mt-3 italic">To decrypt this message later, copy it, then type:<br /><span className="text-cyan mt-1 inline-block">decrypt [paste your copied text here]</span></p>
                )}
              </div>
            );
          } catch (e) {
            output = <div className="history-output font-inter" style={{ color: '#ff5f56' }}>✖ Error processing text. Ensure valid key.</div>;
          }
        }
        break;

      default:
        output = (
          <div className="history-output text-dim font-inter">
            <span style={{ color: '#ff5f56' }}>command not found</span>: <span className="font-mono text-main">{cmd}</span>
          </div>
        );
    }

    if (output) {
      pushHistory({ type: 'output', content: output });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (!input.trim()) return;
      executeCommand(input);
      setCmdList(prev => [input, ...prev]);
      setHistoryIdx(-1);
      setInput('');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (historyIdx < cmdList.length - 1) {
        const nextIdx = historyIdx + 1;
        setHistoryIdx(nextIdx);
        setInput(cmdList[nextIdx]);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIdx > 0) {
        const nextIdx = historyIdx - 1;
        setHistoryIdx(nextIdx);
        setInput(cmdList[nextIdx]);
      } else if (historyIdx === 0) {
        setHistoryIdx(-1);
        setInput('');
      }
    }
  };

  return (
    <div className="terminal-container">
      <div className="terminal-box">
        {/* Header Ribbon */}
        <div className="terminal-header">
          <div className="mac-dots">
            <div className="mac-dot close"></div>
            <div className="mac-dot minimize"></div>
            <div className="mac-dot maximize"></div>
          </div>
          <div className="header-title">SESSION: ZSH - 80x24</div>
        </div>

        {/* Console / Output Area */}
        <div className="terminal-content" ref={containerRef}>
          {history.map((h) => (
            <div key={h.id} className="history-item">
              {h.type === 'command' && (
                <div className="history-input">
                  {h.content} <span className="text-main font-mono font-bold" style={{ marginLeft: '12px' }}>{h.command}</span>
                </div>
              )}
              {h.type === 'output' && h.content}
              {h.type === 'boot' && h.content}
            </div>
          ))}
          <div className="history-input mt-4">
            <Prompt />
          </div>
        </div>

        {/* Input Box Bottom Area */}
        <div className="terminal-footer">
          <div className="input-box">
            <input
              type="text"
              className="input-field"
              placeholder="Type a command..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              spellCheck={false}
              autoComplete="off"
            />
            <div className="enter-badge uppercase">ENTER</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
