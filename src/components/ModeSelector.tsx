import React from 'react';
import { StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { PerformanceMode } from '../types';
import { COLORS } from '../theme/colors';

interface ModeSelectorProps {
  currentMode: PerformanceMode;
  onSelectMode: (mode: PerformanceMode) => void;
}

export const ModeSelector: React.FC<ModeSelectorProps> = ({ currentMode, onSelectMode }) => {
  const modes: { id: PerformanceMode; title: string; subtitle: string; icon: any; grad: readonly [string, string] }[] = [
    {
      id: 'beast',
      title: 'BEAST MODE',
      subtitle: 'Mở khóa 120 FPS',
      icon: 'fire',
      grad: COLORS.beastGrad,
    },
    {
      id: 'esports',
      title: 'E-SPORTS PRO',
      subtitle: 'Hạ Ping & Ổn định',
      icon: 'shield',
      grad: COLORS.esportsGrad,
    },
    {
      id: 'eco',
      title: 'ECO COOLING',
      subtitle: 'Mát máy 35°C & Tiết kiệm',
      icon: 'leaf',
      grad: COLORS.ecoGrad,
    },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>CHẾ ĐỘ HIỆU NĂNG</Text>
      <View style={styles.row}>
        {modes.map((m) => {
          const isActive = currentMode === m.id;
          return (
            <TouchableOpacity
              key={m.id}
              activeOpacity={0.8}
              onPress={() => onSelectMode(m.id)}
              style={styles.cardWrapper}
            >
              <LinearGradient
                colors={isActive ? m.grad : ['#121828', '#0C111C']}
                style={[
                  styles.card,
                  isActive && styles.activeCard,
                ]}
              >
                <FontAwesome
                  name={m.icon}
                  size={18}
                  color={isActive ? '#FFF' : COLORS.textSub}
                  style={styles.icon}
                />
                <Text style={[styles.title, isActive && styles.activeText]}>
                  {m.title}
                </Text>
                <Text style={[styles.subtitle, isActive && styles.activeSub]}>
                  {m.subtitle}
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginHorizontal: 12,
    marginVertical: 10,
  },
  sectionTitle: {
    color: COLORS.textSub,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.2,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  row: {
    flexDirection: 'row',
    gap: 8,
  },
  cardWrapper: {
    flex: 1,
  },
  card: {
    borderRadius: 12,
    padding: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.borderDark,
    minHeight: 88,
    justifyContent: 'center',
  },
  activeCard: {
    borderColor: '#FFF',
    elevation: 6,
  },
  icon: {
    marginBottom: 4,
  },
  title: {
    fontSize: 11,
    fontWeight: '800',
    color: COLORS.textMain,
    textAlign: 'center',
  },
  activeText: {
    color: '#FFF',
  },
  subtitle: {
    fontSize: 9,
    color: COLORS.textMuted,
    textAlign: 'center',
    marginTop: 2,
    fontWeight: '600',
  },
  activeSub: {
    color: 'rgba(255, 255, 255, 0.85)',
  },
});