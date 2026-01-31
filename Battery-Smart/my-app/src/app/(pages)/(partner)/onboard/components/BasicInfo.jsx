import { User, Phone, Mail, Building2 } from 'lucide-react';
import FormSection from './FormSection';
import FormInput from './FormInput';

export default function BasicInfo({ data, onChange }) {
  return (
    <FormSection 
      title="Basic Information" 
      description="Enter the partner's personal details"
    >
      <FormInput
        label="Full Name"
        placeholder="e.g. Rahul Sharma"
        icon={User}
        required
        value={data.name}
        onChange={(e) => onChange('name', e.target.value)}
      />
      <FormInput
        label="Phone Number"
        type="tel"
        placeholder="+91"
        icon={Phone}
        required
        value={data.phone}
        onChange={(e) => onChange('phone', e.target.value)}
      />
      <FormInput
        label="Email Address"
        type="email"
        placeholder="rahul@example.com"
        icon={Mail}
        value={data.email}
        onChange={(e) => onChange('email', e.target.value)}
      />
    </FormSection>
  );
}
