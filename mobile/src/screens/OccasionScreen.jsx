import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Linking, ActivityIndicator } from 'react-native';
import { getOccasions } from '../services/api';

export default function OccasionScreen() {
  const [occasions, setOccasions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getOccasions()
      .then(r => setOccasions(r.data.occasions || r.data || []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function sendWish(occasion) {
    const msg = encodeURIComponent(`Wishing you a wonderful ${occasion.name}! 🎉\n— Shared via PinnacleIQ`);
    Linking.openURL(`whatsapp://send?text=${msg}`);
  }

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color="#0B1628" />;
  if (error)   return <View style={s.center}><Text style={s.err}>⚠️ {error}</Text><Text style={s.hint}>Is the backend running on port 8010?</Text></View>;

  return (
    <FlatList
      data={occasions}
      keyExtractor={o => String(o.id)}
      contentContainerStyle={{ padding: 16 }}
      renderItem={({ item }) => (
        <View style={s.card}>
          <View style={s.row}>
            <Text style={s.icon}>{item.icon || '🎉'}</Text>
            <View style={{ flex: 1 }}>
              <Text style={s.name}>{item.name}</Text>
              <Text style={s.date}>{item.date}</Text>
            </View>
            <TouchableOpacity style={s.btn} onPress={() => sendWish(item)}>
              <Text style={s.btnTxt}>Send Wish</Text>
            </TouchableOpacity>
          </View>
          {item.description && <Text style={s.desc}>{item.description}</Text>}
        </View>
      )}
    />
  );
}

const s = StyleSheet.create({
  card:   { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 4, elevation: 1 },
  row:    { flexDirection: 'row', alignItems: 'center', gap: 12 },
  icon:   { fontSize: 28 },
  name:   { fontSize: 14, fontWeight: '700', color: '#0B1628' },
  date:   { fontSize: 12, color: '#6B7280', marginTop: 2 },
  desc:   { fontSize: 12, color: '#6B7280', marginTop: 10, lineHeight: 18 },
  btn:    { backgroundColor: '#25D366', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 8 },
  btnTxt: { color: '#fff', fontWeight: '700', fontSize: 12 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  err:    { fontSize: 14, color: '#EF4444', fontWeight: '600', textAlign: 'center' },
  hint:   { fontSize: 12, color: '#6B7280', marginTop: 8, textAlign: 'center' },
});
