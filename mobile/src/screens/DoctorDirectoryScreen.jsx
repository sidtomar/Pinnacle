import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getDoctors } from '../services/api';

function mapDoctor(d) {
  return {
    ...d,
    id:       d.id,
    name:     d.name || 'Unknown',
    spec:     d.specialty || d.spec || '—',
    city:     d.city || '—',
    score:    d.engagement_score || d.pinnacle_score || 0,
    init:     (d.name || 'XX').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase(),
  };
}

export default function DoctorDirectoryScreen() {
  const [doctors, setDoctors] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigation = useNavigation();

  useEffect(() => {
    getDoctors()
      .then(r => {
        const raw = r.data.doctors || [];
        const mapped = raw.map(mapDoctor);
        setDoctors(mapped);
        setFiltered(mapped);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function search(q) {
    setQuery(q);
    const lq = q.toLowerCase();
    setFiltered(doctors.filter(d =>
      d.name.toLowerCase().includes(lq) ||
      d.spec.toLowerCase().includes(lq) ||
      d.city.toLowerCase().includes(lq)
    ));
  }

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color="#0B1628" />;
  if (error)   return <View style={s.center}><Text style={s.err}>⚠️ {error}</Text><Text style={s.errHint}>Is the backend running on port 8010?</Text></View>;

  return (
    <View style={s.container}>
      <View style={s.searchWrap}>
        <TextInput
          style={s.search}
          placeholder="Search doctors, specialty, city…"
          value={query}
          onChangeText={search}
        />
      </View>
      <Text style={s.count}>{filtered.length} doctors</Text>
      <FlatList
        data={filtered}
        keyExtractor={d => String(d.id)}
        contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 16 }}
        renderItem={({ item: d }) => (
          <TouchableOpacity style={s.card} onPress={() => navigation.navigate('Doctor360', { doctor: d })}>
            <View style={s.avatar}>
              <Text style={s.initials}>{d.init}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={s.name}>{d.name}</Text>
              <Text style={s.meta}>{d.spec} · {d.city}</Text>
            </View>
            <View style={[s.scoreBadge, { backgroundColor: d.score >= 70 ? '#D1FAE5' : '#FEF3C7' }]}>
              <Text style={[s.scoreText, { color: d.score >= 70 ? '#065F46' : '#92400E' }]}>{d.score}</Text>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const s = StyleSheet.create({
  container:   { flex: 1, backgroundColor: '#F9FAFB' },
  searchWrap:  { padding: 16, paddingBottom: 8 },
  search:      { backgroundColor: '#fff', borderRadius: 10, padding: 12, borderWidth: 1, borderColor: '#E5E7EB', fontSize: 14 },
  count:       { fontSize: 12, color: '#6B7280', paddingHorizontal: 16, marginBottom: 8 },
  card:        { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 10, flexDirection: 'row', alignItems: 'center', gap: 12, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 1 },
  avatar:      { width: 40, height: 40, borderRadius: 10, backgroundColor: '#EBF0F8', justifyContent: 'center', alignItems: 'center' },
  initials:    { fontSize: 13, fontWeight: '800', color: '#0B1628' },
  name:        { fontSize: 13, fontWeight: '700', color: '#0B1628' },
  meta:        { fontSize: 11, color: '#6B7280', marginTop: 2 },
  scoreBadge:  { borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4 },
  scoreText:   { fontSize: 13, fontWeight: '800' },
  center:      { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  err:         { fontSize: 14, color: '#EF4444', fontWeight: '600', textAlign: 'center' },
  errHint:     { fontSize: 12, color: '#6B7280', marginTop: 8, textAlign: 'center' },
});
