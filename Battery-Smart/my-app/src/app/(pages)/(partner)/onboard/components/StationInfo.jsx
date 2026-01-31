import { MapPin, Navigation, Map } from 'lucide-react';
import FormSection from './FormSection';
import FormInput from './FormInput';

export default function StationInfo({ data, onChange }) {
  return (
    <FormSection 
      title="Station Details" 
      description="Location and address of the swap station"
    >
      <div className="md:col-span-2">
        <FormInput
          label="Station Name"
          placeholder="e.g. Koramangala Hub 1"
          required
          value={data.stationName}
          onChange={(e) => onChange('stationName', e.target.value)}
        />
      </div>
      <div className="md:col-span-2">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormInput
            label="Latitude"
            placeholder="12.9716° N"
            icon={MapPin}
            required
            value={data.address}
            onChange={(e) => onChange('address', e.target.value)}
          />
          <FormInput
            label="Longitude"
            placeholder="77.6409° E"
            icon={MapPin}
            required
            value={data.address}
            onChange={(e) => onChange('address', e.target.value)}
          />
        </div>
      </div>
      <FormInput
        label="City"
        placeholder="e.g. Bengaluru"
        icon={Map}
        required
        value={data.city}
        onChange={(e) => onChange('city', e.target.value)}
      />
      <FormInput
        label="State"
        placeholder="e.g. Karnataka"
        icon={Map}
        required
        value={data.state}
        onChange={(e) => onChange('state', e.target.value)}
      />
      <FormInput
        label="Pincode"
        placeholder="560034"
        icon={Navigation}
        required
        value={data.pincode}
        onChange={(e) => onChange('pincode', e.target.value)}
      />
    </FormSection>
  );
}
