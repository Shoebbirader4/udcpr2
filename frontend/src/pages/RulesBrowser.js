import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Book, Filter, X } from 'lucide-react';
import api from '../api/client';

export default function RulesBrowser() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRule, setSelectedRule] = useState(null);

  // Fetch rules from backend
  const { data: rulesData, isLoading } = useQuery({
    queryKey: ['rules', searchQuery, selectedJurisdiction],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      if (selectedJurisdiction !== 'all') params.append('jurisdiction', selectedJurisdiction);
      
      const response = await api.get(`/rules?${params.toString()}`);
      return response.data;
    }
  });

  const rules = Array.isArray(rulesData) ? rulesData : [];

  // Filter by category
  const filteredRules = selectedCategory === 'all' 
    ? rules 
    : rules.filter(rule => getCategoryFromClause(rule.clause_number) === selectedCategory);

  const categories = [
    { id: 'all', name: 'All Categories' },
    { id: 'fsi', name: 'FSI & Development Rights' },
    { id: 'setback', name: 'Setbacks & Open Space' },
    { id: 'parking', name: 'Parking' },
    { id: 'height', name: 'Height Restrictions' },
    { id: 'fire', name: 'Fire Safety' },
    { id: 'accessibility', name: 'Accessibility' },
    { id: 'environment', name: 'Environmental' },
    { id: 'heritage', name: 'Heritage' }
  ];

  function getCategoryFromClause(clauseNumber) {
    if (!clauseNumber) return 'other';
    const chapter = clauseNumber.split('.')[0];
    const categoryMap = {
      '3': 'fsi',
      '4': 'setback',
      '5': 'parking',
      '7': 'height',
      '8': 'fire',
      '9': 'accessibility',
      '10': 'environment',
      '11': 'heritage',
      '12': 'environment'
    };
    return categoryMap[chapter] || 'other';
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Book size={24} className="text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">UDCPR Rules Browser</h1>
            </div>
            <button
              onClick={() => window.history.back()}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="Search rules by keyword, clause number, or description..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                  >
                    <X size={20} />
                  </button>
                )}
              </div>
            </div>

            {/* Jurisdiction Filter */}
            <div>
              <select
                value={selectedJurisdiction}
                onChange={(e) => setSelectedJurisdiction(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Jurisdictions</option>
                <option value="maharashtra_udcpr">Maharashtra UDCPR</option>
                <option value="mumbai_dcpr">Mumbai DCPR 2034</option>
              </select>
            </div>
          </div>

          {/* Category Filters */}
          <div className="mt-4 flex items-center gap-2 flex-wrap">
            <Filter size={16} className="text-gray-500" />
            {categories.map(category => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-3 py-1 rounded-full text-sm ${
                  selectedCategory === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Rules List */}
          <div className="lg:col-span-2 space-y-4">
            {isLoading ? (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <p className="text-gray-500">Loading rules...</p>
              </div>
            ) : filteredRules.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <Book size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600 mb-2">No rules found</p>
                <p className="text-sm text-gray-500">
                  {searchQuery ? 'Try a different search term' : 'No rules available in the database'}
                </p>
              </div>
            ) : (
              filteredRules.map(rule => (
                <div
                  key={rule.rule_id}
                  onClick={() => setSelectedRule(rule)}
                  className={`bg-white rounded-lg shadow p-4 cursor-pointer transition ${
                    selectedRule?.rule_id === rule.rule_id
                      ? 'ring-2 ring-blue-500'
                      : 'hover:shadow-md'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded">
                          {rule.clause_number}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded ${
                          rule.jurisdiction === 'maharashtra_udcpr'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-purple-100 text-purple-700'
                        }`}>
                          {rule.jurisdiction === 'maharashtra_udcpr' ? 'UDCPR' : 'Mumbai DCPR'}
                        </span>
                        {rule.ambiguous && (
                          <span className="text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-700">
                            ⚠️ Ambiguous
                          </span>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-900 mb-1">
                        {rule.title}
                      </h3>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {rule.clause_text}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Rule Detail Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              {selectedRule ? (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-lg">Rule Details</h3>
                    <button
                      onClick={() => setSelectedRule(null)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X size={20} />
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Clause Number</p>
                      <p className="font-mono text-sm bg-gray-50 px-3 py-2 rounded">
                        {selectedRule.clause_number}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-500 mb-1">Title</p>
                      <p className="font-semibold">{selectedRule.title}</p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-500 mb-1">Jurisdiction</p>
                      <p className="text-sm">
                        {selectedRule.jurisdiction === 'maharashtra_udcpr' 
                          ? 'Maharashtra UDCPR' 
                          : 'Mumbai DCPR 2034'}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-gray-500 mb-1">Full Text</p>
                      <p className="text-sm bg-gray-50 p-3 rounded">
                        {selectedRule.clause_text}
                      </p>
                    </div>

                    {selectedRule.parsed?.rule_logic && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Rule Logic</p>
                        <pre className="text-xs bg-gray-50 p-3 rounded overflow-x-auto">
                          {JSON.stringify(selectedRule.parsed.rule_logic, null, 2)}
                        </pre>
                      </div>
                    )}

                    {selectedRule.source_pdf && (
                      <div>
                        <p className="text-sm text-gray-500 mb-1">Source</p>
                        <p className="text-xs text-gray-600">
                          {selectedRule.source_pdf.filename}, Page {selectedRule.source_pdf.page}
                        </p>
                      </div>
                    )}

                    {selectedRule.ambiguous && (
                      <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                        <p className="text-sm font-medium text-yellow-800 mb-1">
                          ⚠️ Ambiguous Rule
                        </p>
                        <p className="text-xs text-yellow-700">
                          {selectedRule.ambiguity_reason}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Book size={48} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 text-sm">
                    Select a rule to view details
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        {!isLoading && rules.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                Showing {filteredRules.length} of {rules.length} rules
              </span>
              <span>
                {rules.filter(r => r.jurisdiction === 'maharashtra_udcpr').length} UDCPR • {' '}
                {rules.filter(r => r.jurisdiction === 'mumbai_dcpr').length} Mumbai DCPR
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
