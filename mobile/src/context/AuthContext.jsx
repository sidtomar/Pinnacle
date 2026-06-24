import React, { createContext, useContext, useState } from 'react';

// Mirrors USERS_DB in PinnacleIQ_Portal.html — PMT users only for mobile
const USERS_DB = [
  { id: 'jijo',          name: 'Jijo Kumar',    email: 'jijo@mankind.in',           role: 'pmt', designation: 'BU Head', division: '3D Mankind', initials: 'JK' },
  { id: 'priya_nair',    name: 'Priya Nair',    email: 'priya.nair@mankind.in',     role: 'pmt', designation: 'Marketing Head', division: '3D Mankind', initials: 'PN' },
  { id: 'rajesh_sharma', name: 'Rajesh Sharma', email: 'rajesh.sharma@mankind.in',  role: 'pmt', designation: 'NSM', division: '', initials: 'RS' },
  { id: 'amit_verma',    name: 'Amit Verma',    email: 'amit.verma@mankind.in',     role: 'pmt', designation: 'BU Head', division: '', initials: 'AV' },
];

const APP_PASSWORD = 'Test';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  function login(email, password) {
    const found = USERS_DB.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (!found) { setError('No account found for this email.'); return false; }
    const expected = found.pwd || APP_PASSWORD;
    if (password !== expected) { setError('Incorrect password.'); return false; }
    setUser(found);
    setError('');
    return true;
  }

  function logout() { setUser(null); }

  return (
    <AuthContext.Provider value={{ user, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() { return useContext(AuthContext); }
