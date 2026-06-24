import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { getContent } from '../services/api';

export default function ContentFeedScreen() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigation = useNavigation();

  useEffect(() => {
    getContent()
      .then(r => {
        const items = r.data.items || r.data.content || r.data || [];
        setPapers(items.filter(p => p.status === 'approved'));
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <ActivityIndicator style={{ flex: 1 }} color="#0B1628" />;
  if (error)   return <View style={s.center}><Text style={s.err}>⚠️ {error}</Text><Text style={s.errHint}>Is the backend running on port 8010?</Text></View>;
  if (!papers.length) return <View style={s.center}><Text style={s.empty}>No approved content yet.</Text><Text style={s.errHint}>Approve articles in the web app first.</Text></View>;

  return (
    <FlatList
      data={papers}
      keyExtractor={p => String(p.id)}
      contentContainerStyle={{ padding: 16 }}
      renderItem={({ item }) => {
        const spec = item.specialty || item.cat || '';
        const therapy = item.therapy_area || '';
        return (
          <TouchableOpacity style={s.card} onPress={() => navigation.navigate('ContentDetail', { paper: item })}>
            <View style={s.tagRow}>
              {spec ? <Text style={s.tag}>{spec}</Text> : null}
              {therapy && therapy.toLowerCase() !== spec.toLowerCase() &&
                <Text style={[s.tag, { backgroundColor: '#FEF3C7', color: '#92400E' }]}>{therapy}</Text>}
            </View>
            <Text style={s.title} numberOfLines={2}>{item.title}</Text>
            <Text style={s.summary} numberOfLines={3}>{item.summary || item.abstract || 'No summary available.'}</Text>
            <View style={s.footer}>
              <Text style={s.readMore}>Read full article →</Text>
            </View>
          </TouchableOpacity>
        );
      }}
    />
  );
}

const s = StyleSheet.create({
  card:     { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  tagRow:   { flexDirection: 'row', gap: 6, marginBottom: 8, flexWrap: 'wrap' },
  tag:      { fontSize: 11, fontWeight: '600', backgroundColor: '#EFF6FF', color: '#1D4ED8', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  title:    { fontSize: 14, fontWeight: '700', color: '#0B1628', marginBottom: 6 },
  summary:  { fontSize: 12, color: '#6B7280', lineHeight: 18 },
  footer:   { marginTop: 12, borderTopWidth: 1, borderTopColor: '#F3F4F6', paddingTop: 10 },
  readMore: { fontSize: 13, color: '#F59E0B', fontWeight: '600' },
  center:   { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  err:      { fontSize: 14, color: '#EF4444', fontWeight: '600', textAlign: 'center' },
  errHint:  { fontSize: 12, color: '#6B7280', marginTop: 8, textAlign: 'center' },
  empty:    { fontSize: 14, color: '#374151', fontWeight: '600', textAlign: 'center' },
});
