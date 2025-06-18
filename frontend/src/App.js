import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Asset type options
const ASSET_TYPES = [
  { value: 'email_campaign', label: 'Email Campaign', icon: '📧', description: 'Create compelling email marketing campaigns' },
  { value: 'social_media_ad', label: 'Social Media Ad', icon: '📱', description: 'Generate high-converting social media ads' },
  { value: 'landing_page', label: 'Landing Page', icon: '🖼️', description: 'Build persuasive landing page copy' },
  { value: 'sales_funnel', label: 'Sales Funnel', icon: '🎯', description: 'Design complete sales funnel strategy' },
  { value: 'blog_post', label: 'Blog Post', icon: '📝', description: 'Write engaging blog content' },
  { value: 'press_release', label: 'Press Release', icon: '📰', description: 'Create professional press releases' }
];

const TONE_OPTIONS = [
  'professional', 'friendly', 'casual', 'authoritative', 'conversational', 
  'energetic', 'trustworthy', 'innovative', 'luxury', 'approachable'
];

// Components
const Header = ({ user, onNavigate, currentView }) => (
  <header className="bg-white shadow-sm border-b border-gray-200">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-gray-900">AI Marketing Hub</h1>
        </div>
        <nav className="flex space-x-8">
          <button
            onClick={() => onNavigate('dashboard')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              currentView === 'dashboard' 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => onNavigate('generate')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              currentView === 'generate' 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Generate Asset
          </button>
          <button
            onClick={() => onNavigate('assets')}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
              currentView === 'assets' 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            My Assets
          </button>
        </nav>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            Credits: <span className="font-semibold text-blue-600">{user?.credits || 0}</span>
          </div>
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {user?.name?.charAt(0) || 'U'}
          </div>
        </div>
      </div>
    </div>
  </header>
);

const Dashboard = ({ stats, onNavigate }) => (
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {/* Welcome Section */}
    <div className="mb-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome back!</h2>
      <p className="text-gray-600">Generate high-quality marketing assets with AI in seconds.</p>
    </div>

    {/* Stats Cards */}
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center">
          <div className="p-2 bg-blue-100 rounded-lg">
            <span className="text-2xl">🎯</span>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Total Assets</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.total_assets || 0}</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center">
          <div className="p-2 bg-green-100 rounded-lg">
            <span className="text-2xl">⚡</span>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Credits Used</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.credits_used || 0}</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center">
          <div className="p-2 bg-purple-100 rounded-lg">
            <span className="text-2xl">💎</span>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Current Plan</p>
            <p className="text-2xl font-bold text-gray-900 capitalize">{stats?.user?.plan || 'Free'}</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center">
          <div className="p-2 bg-orange-100 rounded-lg">
            <span className="text-2xl">🔥</span>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-600">Credits Left</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.user?.credits || 0}</p>
          </div>
        </div>
      </div>
    </div>

    {/* Quick Actions */}
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => onNavigate('generate')}
          className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200 text-left"
        >
          <div className="text-2xl mb-2">✨</div>
          <h4 className="font-medium text-gray-900">Generate New Asset</h4>
          <p className="text-sm text-gray-600">Create marketing content with AI</p>
        </button>
        
        <button
          onClick={() => onNavigate('assets')}
          className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200 text-left"
        >
          <div className="text-2xl mb-2">📁</div>
          <h4 className="font-medium text-gray-900">View All Assets</h4>
          <p className="text-sm text-gray-600">Browse your generated content</p>
        </button>
        
        <button className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200 text-left opacity-75">
          <div className="text-2xl mb-2">⬆️</div>
          <h4 className="font-medium text-gray-900">Upgrade Plan</h4>
          <p className="text-sm text-gray-600">Get more credits and features</p>
        </button>
      </div>
    </div>

    {/* Asset Types Overview */}
    {stats?.asset_counts && (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Asset Portfolio</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {ASSET_TYPES.map((type) => (
            <div key={type.value} className="text-center">
              <div className="text-2xl mb-2">{type.icon}</div>
              <p className="text-sm font-medium text-gray-900">{type.label}</p>
              <p className="text-lg font-bold text-blue-600">{stats.asset_counts[type.value] || 0}</p>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);

const GenerateAsset = ({ onGenerate, isGenerating }) => {
  const [formData, setFormData] = useState({
    asset_type: '',
    business_name: '',
    product_service: '',
    target_audience: '',
    tone: 'professional',
    objectives: [],
    additional_context: ''
  });
  
  const [currentStep, setCurrentStep] = useState(1);

  const handleSubmit = (e) => {
    e.preventDefault();
    onGenerate(formData);
  };

  const nextStep = () => setCurrentStep(currentStep + 1);
  const prevStep = () => setCurrentStep(currentStep - 1);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Generate Marketing Asset</h2>
          <div className="flex items-center space-x-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className={`flex items-center ${step < 3 ? 'flex-1' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep >= step ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
                }`}>
                  {step}
                </div>
                {step < 3 && <div className={`flex-1 h-1 mx-4 ${currentStep > step ? 'bg-blue-500' : 'bg-gray-200'}`} />}
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Step 1: Asset Type Selection */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Choose Asset Type</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ASSET_TYPES.map((type) => (
                  <label key={type.value} className="cursor-pointer">
                    <input
                      type="radio"
                      name="asset_type"
                      value={type.value}
                      checked={formData.asset_type === type.value}
                      onChange={(e) => setFormData({...formData, asset_type: e.target.value})}
                      className="sr-only"
                    />
                    <div className={`p-4 border-2 rounded-lg transition-all duration-200 ${
                      formData.asset_type === type.value 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <div className="flex items-start space-x-3">
                        <span className="text-2xl">{type.icon}</span>
                        <div>
                          <h4 className="font-medium text-gray-900">{type.label}</h4>
                          <p className="text-sm text-gray-600">{type.description}</p>
                        </div>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: Business Details */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Business Details</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Business Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.business_name}
                  onChange={(e) => setFormData({...formData, business_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your business name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product/Service *
                </label>
                <textarea
                  required
                  value={formData.product_service}
                  onChange={(e) => setFormData({...formData, product_service: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Describe your product or service"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience *
                </label>
                <input
                  type="text"
                  required
                  value={formData.target_audience}
                  onChange={(e) => setFormData({...formData, target_audience: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Small business owners, Tech professionals, Parents"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tone & Style
                </label>
                <select
                  value={formData.tone}
                  onChange={(e) => setFormData({...formData, tone: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {TONE_OPTIONS.map((tone) => (
                    <option key={tone} value={tone}>
                      {tone.charAt(0).toUpperCase() + tone.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Step 3: Campaign Details */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Campaign Details</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Objectives
                </label>
                <textarea
                  value={formData.objectives.join(', ')}
                  onChange={(e) => setFormData({...formData, objectives: e.target.value.split(', ').filter(obj => obj.trim())})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="2"
                  placeholder="e.g., Increase brand awareness, Generate leads, Drive sales"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Context
                </label>
                <textarea
                  value={formData.additional_context}
                  onChange={(e) => setFormData({...formData, additional_context: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Any additional information, special requirements, or context..."
                />
              </div>

              {/* Preview */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Generation Preview</h4>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Asset Type:</strong> {ASSET_TYPES.find(t => t.value === formData.asset_type)?.label}</p>
                  <p><strong>Business:</strong> {formData.business_name}</p>
                  <p><strong>Target:</strong> {formData.target_audience}</p>
                  <p><strong>Tone:</strong> {formData.tone}</p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button
              type="button"
              onClick={prevStep}
              disabled={currentStep === 1}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {currentStep < 3 ? (
              <button
                type="button"
                onClick={nextStep}
                disabled={
                  (currentStep === 1 && !formData.asset_type) ||
                  (currentStep === 2 && (!formData.business_name || !formData.product_service || !formData.target_audience))
                }
                className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={isGenerating}
                className="px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? 'Generating...' : 'Generate Asset'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

const AssetList = ({ assets, onViewAsset, onDeleteAsset }) => (
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div className="mb-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">My Assets</h2>
      <p className="text-gray-600">Manage your generated marketing content</p>
    </div>

    {assets.length === 0 ? (
      <div className="text-center py-12">
        <div className="text-4xl mb-4">📝</div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No assets yet</h3>
        <p className="text-gray-600 mb-4">Start by generating your first marketing asset</p>
      </div>
    ) : (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {assets.map((asset) => (
          <div key={asset.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">
                  {ASSET_TYPES.find(t => t.value === asset.asset_type)?.icon}
                </span>
                <div>
                  <h3 className="font-semibold text-gray-900">{asset.title}</h3>
                  <p className="text-sm text-gray-600">
                    {ASSET_TYPES.find(t => t.value === asset.asset_type)?.label}
                  </p>
                </div>
              </div>
              <button
                onClick={() => onDeleteAsset(asset.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Delete
              </button>
            </div>
            
            <div className="mb-4">
              <p className="text-sm text-gray-600 line-clamp-3">
                {asset.content.substring(0, 200)}...
              </p>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="text-xs text-gray-500">
                Created {new Date(asset.created_at).toLocaleDateString()}
              </div>
              <button
                onClick={() => onViewAsset(asset)}
                className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
              >
                View Full
              </button>
            </div>
          </div>
        ))}
      </div>
    )}
  </div>
);

const AssetViewer = ({ asset, onClose }) => (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">
            {ASSET_TYPES.find(t => t.value === asset.asset_type)?.icon}
          </span>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{asset.title}</h2>
            <p className="text-sm text-gray-600">
              {ASSET_TYPES.find(t => t.value === asset.asset_type)?.label}
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
        <div className="prose max-w-none">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
            {asset.content}
          </pre>
        </div>
        
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex space-x-4">
            <button
              onClick={() => navigator.clipboard.writeText(asset.content)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Copy to Clipboard
            </button>
            <button
              onClick={() => {
                const blob = new Blob([asset.content], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${asset.title}.txt`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Download
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Main App Component
function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [assets, setAssets] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Load initial data
  useEffect(() => {
    loadUserProfile();
    loadAssets();
    loadDashboardStats();
  }, []);

  const loadUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/user/profile`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to load user profile:', error);
      setError('Failed to load user profile');
    }
  };

  const loadAssets = async () => {
    try {
      const response = await axios.get(`${API}/assets`);
      setAssets(response.data);
    } catch (error) {
      console.error('Failed to load assets:', error);
    }
  };

  const loadDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    }
  };

  const handleGenerateAsset = async (formData) => {
    setIsGenerating(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API}/assets/generate`, formData);
      
      // Refresh data
      await loadUserProfile();
      await loadAssets();
      await loadDashboardStats();
      
      // Navigate to assets view to show the new asset
      setCurrentView('assets');
      
    } catch (error) {
      console.error('Failed to generate asset:', error);
      setError(error.response?.data?.detail || 'Failed to generate asset');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteAsset = async (assetId) => {
    if (!window.confirm('Are you sure you want to delete this asset?')) return;
    
    try {
      await axios.delete(`${API}/assets/${assetId}`);
      await loadAssets();
      await loadDashboardStats();
    } catch (error) {
      console.error('Failed to delete asset:', error);
      setError('Failed to delete asset');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header 
        user={user} 
        onNavigate={setCurrentView} 
        currentView={currentView}
      />
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mx-4 mt-4">
          {error}
          <button 
            onClick={() => setError(null)}
            className="float-right font-bold"
          >
            ×
          </button>
        </div>
      )}

      {currentView === 'dashboard' && (
        <Dashboard 
          stats={dashboardStats} 
          onNavigate={setCurrentView}
        />
      )}

      {currentView === 'generate' && (
        <GenerateAsset 
          onGenerate={handleGenerateAsset}
          isGenerating={isGenerating}
        />
      )}

      {currentView === 'assets' && (
        <AssetList 
          assets={assets}
          onViewAsset={setSelectedAsset}
          onDeleteAsset={handleDeleteAsset}
        />
      )}

      {selectedAsset && (
        <AssetViewer 
          asset={selectedAsset}
          onClose={() => setSelectedAsset(null)}
        />
      )}
    </div>
  );
}

export default App;