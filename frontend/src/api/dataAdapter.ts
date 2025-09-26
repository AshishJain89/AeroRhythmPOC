// Safe data adapter with fallbacks
export const adaptCrew = (backendCrew: any) => {
  if (!backendCrew) return null;
  
  return {
    id: backendCrew.id || '',
    firstName: backendCrew.first_name || backendCrew.firstName || 'Unknown',
    lastName: backendCrew.last_name || backendCrew.lastName || 'Crew',
    employeeNumber: backendCrew.employee_id || backendCrew.employeeNumber || 'N/A',
    position: backendCrew.position || 'Unknown',
    homeBase: backendCrew.home_base || backendCrew.homeBase || 'Unknown',
    status: backendCrew.status || 'available',
    licenseExpiry: backendCrew.license_expiry || '2026-12-31',
    qualifications: backendCrew.qualifications || [],
    createdAt: backendCrew.created_at || new Date().toISOString()
  };
};

export const adaptFlight = (backendFlight: any) => {
  if (!backendFlight) return null;
  
  return {
    id: backendFlight.id || '',
    flightNumber: backendFlight.flight_number || backendFlight.flightNumber || 'N/A',
    origin: backendFlight.origin || 'Unknown',
    destination: backendFlight.destination || 'Unknown',
    departureTime: backendFlight.departure_time || backendFlight.departureTime,
    arrivalTime: backendFlight.arrival_time || backendFlight.arrivalTime,
    aircraftType: backendFlight.aircraft_type || backendFlight.aircraftType || 'Unknown',
    status: backendFlight.status || 'scheduled',
    createdAt: backendFlight.created_at || new Date().toISOString()
  };
};

// Add safe array mapping
export const safeMap = <T, U>(array: any[] | undefined, adapter: (item: any) => U): U[] => {
  if (!array || !Array.isArray(array)) return [];
  return array.map(adapter).filter(Boolean) as U[];
};