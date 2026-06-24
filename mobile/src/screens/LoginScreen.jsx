import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image, KeyboardAvoidingView, Platform } from 'react-native';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen() {
  const { login, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <KeyboardAvoidingView style={s.container} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={s.card}>
        <Text style={s.brand}>Pinnacle<Text style={s.iq}>IQ</Text></Text>
        <Text style={s.sub}>Doctor Intelligence Platform</Text>

        <Text style={s.label}>Email</Text>
        <TextInput
          style={s.input}
          placeholder="you@mankind.in"
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
        />

        <Text style={s.label}>Password</Text>
        <TextInput
          style={s.input}
          placeholder="Password"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
        />

        {!!error && <Text style={s.error}>{error}</Text>}

        <TouchableOpacity style={s.btn} onPress={() => login(email, password)}>
          <Text style={s.btnTxt}>Sign In</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0B1628', justifyContent: 'center', padding: 24 },
  card:      { backgroundColor: '#fff', borderRadius: 16, padding: 28 },
  brand:     { fontSize: 28, fontWeight: '800', color: '#0B1628', textAlign: 'center' },
  iq:        { color: '#F59E0B' },
  sub:       { fontSize: 12, color: '#6B7280', textAlign: 'center', marginBottom: 28 },
  label:     { fontSize: 12, fontWeight: '600', color: '#374151', marginBottom: 4 },
  input:     { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 12, marginBottom: 16, fontSize: 14 },
  error:     { color: '#EF4444', fontSize: 12, marginBottom: 12 },
  btn:       { backgroundColor: '#0B1628', borderRadius: 8, padding: 14, alignItems: 'center' },
  btnTxt:    { color: '#fff', fontWeight: '700', fontSize: 15 },
});
