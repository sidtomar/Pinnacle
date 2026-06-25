import React, { useState, useRef } from 'react';
import { View, Text, TouchableOpacity, Animated, StyleSheet, StatusBar, Platform } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';

import TodayScreen           from '../screens/TodayScreen';
import ContentFeedScreen     from '../screens/ContentFeedScreen';
import ContentDetailScreen   from '../screens/ContentDetailScreen';
import OccasionScreen        from '../screens/OccasionScreen';
import DoctorDirectoryScreen from '../screens/DoctorDirectoryScreen';
import Doctor360Screen       from '../screens/Doctor360Screen';
import DrawerContent         from './DrawerContent';

const Stack        = createNativeStackNavigator();
const NAVY         = '#0B1628';
const GOLD         = '#F59E0B';
const DRAWER_WIDTH = 280;

const TABS = [
  { key: 'today',     label: "Today's Tasks",    icon: 'today-outline' },
  { key: 'content',   label: 'Content Library',  icon: 'newspaper-outline' },
  { key: 'doctors',   label: 'Doctor Directory', icon: 'people-outline' },
  { key: 'occasions', label: 'Occasion Hub',     icon: 'calendar-outline' },
];

function MainLayout() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab]   = useState('today');
  const [drawerOpen, setDrawerOpen] = useState(false);

  const slideAnim   = useRef(new Animated.Value(-DRAWER_WIDTH)).current;
  const overlayAnim = useRef(new Animated.Value(0)).current;

  const tabInfo = TABS.find(t => t.key === activeTab);

  function openDrawer() {
    setDrawerOpen(true);
    Animated.parallel([
      Animated.timing(slideAnim,   { toValue: 0,    duration: 260, useNativeDriver: true }),
      Animated.timing(overlayAnim, { toValue: 0.55, duration: 260, useNativeDriver: true }),
    ]).start();
  }

  function closeDrawer(cb) {
    Animated.parallel([
      Animated.timing(slideAnim,   { toValue: -DRAWER_WIDTH, duration: 210, useNativeDriver: true }),
      Animated.timing(overlayAnim, { toValue: 0,             duration: 210, useNativeDriver: true }),
    ]).start(() => { setDrawerOpen(false); cb && cb(); });
  }

  function navigateTo(tab) { closeDrawer(() => setActiveTab(tab)); }

  function renderScreen() {
    switch (activeTab) {
      case 'today':     return <TodayScreen />;
      case 'content':   return <ContentFeedScreen />;
      case 'doctors':   return <DoctorDirectoryScreen />;
      case 'occasions': return <OccasionScreen />;
    }
  }

  const statusBarHeight = Platform.OS === 'android' ? (StatusBar.currentHeight || 24) : 0;

  return (
    <View style={s.root}>
      <StatusBar barStyle="light-content" backgroundColor={NAVY} />

      {/* Top nav bar */}
      <View style={[s.header, { paddingTop: statusBarHeight }]}>
        <TouchableOpacity onPress={openDrawer} style={s.hamburger} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
          <Ionicons name="menu" size={26} color="#fff" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>{tabInfo?.label}</Text>
        <View style={s.avatar}>
          <Text style={s.avatarTxt}>{user?.initials || '??'}</Text>
        </View>
      </View>

      {/* Screen content */}
      <View style={s.content}>{renderScreen()}</View>

      {/* Dim overlay — tapping closes drawer */}
      {drawerOpen && (
        <TouchableOpacity
          style={StyleSheet.absoluteFill}
          activeOpacity={1}
          onPress={() => closeDrawer()}
        >
          <Animated.View style={[s.overlay, { opacity: overlayAnim }]} />
        </TouchableOpacity>
      )}

      {/* Sliding drawer panel */}
      <Animated.View
        style={[s.drawer, { transform: [{ translateX: slideAnim }] }]}
        pointerEvents={drawerOpen ? 'auto' : 'none'}
      >
        <DrawerContent
          user={user}
          activeTab={activeTab}
          tabs={TABS}
          onNavigate={navigateTo}
          onLogout={logout}
        />
      </Animated.View>
    </View>
  );
}

export default function AppNavigator() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Main" component={MainLayout} />
      <Stack.Screen
        name="ContentDetail"
        component={ContentDetailScreen}
        options={({ route }) => ({
          headerShown: true,
          headerStyle: { backgroundColor: NAVY },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: '700' },
          title: ((route.params?.paper?.title || 'Article').slice(0, 32) + '...'),
        })}
      />
      <Stack.Screen
        name="Doctor360"
        component={Doctor360Screen}
        options={({ route }) => ({
          headerShown: true,
          headerStyle: { backgroundColor: NAVY },
          headerTintColor: '#fff',
          headerTitleStyle: { fontWeight: '700' },
          title: route.params?.doctor?.name || 'Doctor 360',
        })}
      />
    </Stack.Navigator>
  );
}

const s = StyleSheet.create({
  root:        { flex: 1, backgroundColor: '#F9FAFB' },
  header:      { flexDirection: 'row', alignItems: 'center', backgroundColor: NAVY, paddingHorizontal: 14, paddingBottom: 12 },
  hamburger:   { width: 40, height: 40, justifyContent: 'center', alignItems: 'center' },
  headerTitle: { flex: 1, color: '#fff', fontSize: 17, fontWeight: '700', marginLeft: 6 },
  avatar:      { width: 36, height: 36, borderRadius: 18, backgroundColor: GOLD, justifyContent: 'center', alignItems: 'center' },
  avatarTxt:   { color: '#fff', fontWeight: '800', fontSize: 13 },
  content:     { flex: 1 },
  overlay:     { ...StyleSheet.absoluteFillObject, backgroundColor: '#000' },
  drawer:      { position: 'absolute', top: 0, left: 0, bottom: 0, width: DRAWER_WIDTH, zIndex: 999, elevation: 20 },
});
