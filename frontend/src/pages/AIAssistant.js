import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, BookOpen, Loader } from 'lucide-react';
import axios from 'axios';

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your UDCPR AI Assistant. Ask me anything about Maharashtra UDCPR or Mumbai DCPR regulations.',
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Call RAG service
      const ragUrl = process.env.REACT_APP_RAG_SERVICE_URL || 'http://localhost:8002';
      const response = await axios.post(`${ragUrl}/query`, {
        query: userMessage,
        n_results: 5
      });

      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources || [],
        confidence: response.data.confidence,
        follow_ups: response.data.follow_up_questions || []
      }]);
    } catch (error) {
      console.error('Error querying AI:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the RAG service is running (python ai_services/rag_service.py)',
        sources: []
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowUp = (question) => {
    setInput(question);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Bot size={24} className="text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
          </div>
          <button
            onClick={() => window.history.back()}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
        </div>
      </nav>

      {/* Chat Container */}
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 py-6 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex gap-3 max-w-3xl ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.role === 'user' ? 'bg-blue-600' : 'bg-gray-200'
                }`}>
                  {message.role === 'user' ? (
                    <User size={18} className="text-white" />
                  ) : (
                    <Bot size={18} className="text-gray-700" />
                  )}
                </div>

                {/* Message Content */}
                <div className={`flex-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block px-4 py-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white shadow'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>

                  {/* Sources */}
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 space-y-1">
                      <p className="text-xs text-gray-500 flex items-center gap-1">
                        <BookOpen size={12} />
                        Sources:
                      </p>
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="text-xs bg-gray-50 px-2 py-1 rounded inline-block mr-2">
                          <span className="font-mono text-blue-600">{source.clause_number}</span>
                          {' - '}
                          <span className="text-gray-600">{source.title.substring(0, 40)}...</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Follow-up Questions */}
                  {message.follow_ups && message.follow_ups.length > 0 && (
                    <div className="mt-3 space-y-1">
                      <p className="text-xs text-gray-500">Follow-up questions:</p>
                      {message.follow_ups.map((question, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleFollowUp(question)}
                          className="block text-xs text-left text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          • {question}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Confidence Badge */}
                  {message.confidence && (
                    <div className="mt-1">
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        message.confidence === 'high' ? 'bg-green-100 text-green-700' :
                        message.confidence === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                        {message.confidence} confidence
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="flex gap-3 max-w-3xl">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <Bot size={18} className="text-gray-700" />
                </div>
                <div className="bg-white shadow px-4 py-3 rounded-lg">
                  <Loader size={18} className="animate-spin text-gray-500" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about FSI, setbacks, parking, or any UDCPR regulation..."
              className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send size={18} />
              Send
            </button>
          </div>

          {/* Suggested Questions */}
          <div className="mt-3 flex flex-wrap gap-2">
            <p className="text-xs text-gray-500 w-full">Try asking:</p>
            {[
              "What is the FSI for residential buildings?",
              "Parking requirements for commercial buildings",
              "Setback rules for corner plots",
              "TOD zone benefits"
            ].map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => setInput(suggestion)}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
