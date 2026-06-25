import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const NAVY       = '#0B1628';
const GOLD       = '#F59E0B';
const NAVY_CARD  = '#1E3A5F';
const MUTED      = '#94A3B8';

export default function DrawerContent({ user, activeTab, tabs, onNavigate, onLogout }) {
  return (
    <SafeAreaView style={s.container}>
      {/* Brand */}
      <View style={s.brand}>
        <Text style={s.logo}>Pinnacle<Text style={s.logoIQ}>IQ</Text></Text>
        <Text style={s.logoSub}>Doctor Intelligence Platform</Text>
      </View>

      <View style={s.divider} />

      {/* Nav items */}
      <View style={s.menu}>
        {tabs.map(tab => {
          const active = activeTab === tab.key;
          return (
            <TouchableOpacity
              key={tab.key}
              style={[s.item, active && s.itemActive]}
              onPress={() => onNavigate(tab.key)}
              activeOpacity={0.7}
            >
              <View style={[s.iconBox, active && s.iconBoxActive]}>
                <Ionicons name={tab.icon} size={19} color={active ? NAVY : MUTED} />
              </View>
              <Text style={[s.label, active && s.labelActive]}>{tab.label}</Text>
              {active && <View style={s.bar} />}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* User + logout */}
      <View style={s.footer}>
        <View style={s.divider} />
        <View style={s.userRow}>
          <View style={s.avatar}>
            <Text style={s.avatarTxt}>{user?.initials || '??'}</Text>
          </View>
          <View style={s.userInfo}>
            <Text style={s.userName} numberOfLines={1}>{user?.name || 'User'}</Text>
            <Text style={s.userDes}>{user?.designation || 'BU Head'}</Text>
          </View>
        </View>
        <TouchableOpacity style={s.logout} onPress={onLogout} activeOpacity={0.7}>
          <Ionicons name="log-out-outline" size={17} color={MUTED} />
          <Text style={s.logoutTxt}>Sign Out</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  container:    { flex: 1, backgroundColor: NAVY },
  brand:        { paddingHorizontal: 20, paddingTop: 20, paddingBottom: 12 },
  logo:         { fontSize: 24, fontWeight: '800', color: '#fff' },
  logoIQ:       { color: GOLD },
  logoSub:      { fontSize: 10, color: MUTED, marginTop: 3, letterSpacing: 0.4 },
  divider:      { height: 1, backgroundColor: '#1E3A5F', marginHorizontal: 16 },
  menu:         { flex: 1, paddingTop: 10 },
  item:         { flexDirection: 'row', alignItems: 'center', marginHorizontal: 12, marginVertical: 2, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 11 },
  itemActive:   { backgroundColor: GOLD + '1A' },
  iconBox:      { width: 34, height: 34, borderRadius: 8, backgroundColor: NAVY_CARD, justifyContent: 'center', alignItems: 'center' },
  iconBoxActive:{ backgroundColor: GOLD },
  label:        { flex: 1, marginLeft: 12, fontSize: 14, color: MUTED, fontWeight: '500' },
  labelActive:  { color: GOLD, fontWeight: '700' },
  bar:          { width: 4, height: 22, borderRadius: 2, backgroundColor: GOLD },
  footer:       { paddingHorizontal: 16, paddingBottom: 12 },
  userRow:      { flexDirection: 'row', alignItems: 'center', paddingVertical: 14 },
  avatar:       { width: 40, height: 40, borderRadius: 20, backgroundColor: GOLD, justifyContent: 'center', alignItems: 'center' },
  avatarTxt:    { color: '#fff', fontWeight: '800', fontSize: 14 },
  userInfo:     { flex: 1, marginLeft: 12 },
  userName:     { color: '#fff', fontWeight: '700', fontSize: 14 },
  userDes:      { color: MUTED, fontSize: 12, marginTop: 1 },
  logout:       { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, gap: 8 },
  logoutTxt:    { color: MUTED, fontSize: 14 },
});
