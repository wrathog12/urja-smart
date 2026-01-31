"use client";

import React, { useState } from 'react';
import { ChevronRight } from 'lucide-react';
import BasicInfo from './components/BasicInfo';
import StationInfo from './components/StationInfo';

export default function Onboard() {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    companyName: '',
    stationName: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    accountNumber: '',
    ifsc: '',
    upiId: '',
    gst: ''
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form Submitted:', formData);
    // Add API call here
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-10">
      <div className="max-w-4xl mx-auto p-4 md:p-8 space-y-8">
        
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Partner Onboarding</h1>
          <p className="text-gray-500 mt-1">Register a new station partner and setup payments.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <BasicInfo data={formData} onChange={handleChange} />
          <StationInfo data={formData} onChange={handleChange} />
          
          <div className="flex justify-end pt-4">
            <button 
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-sm"
            >
              Submit Application
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}