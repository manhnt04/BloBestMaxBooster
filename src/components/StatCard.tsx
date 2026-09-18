import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { COLORS } from '../theme/colors';

interface StatCardProps {
  title: string;
  value: string;
  subValue: string;
  percentage: number;
  icon: any;
  color: string;
  accentGradient: readonly [string, string];
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subValue,
  percentage,
  icon,
  color,
  accentGradient,
}) => {
  return (
    <LinearGradient
      colors={['#101728', '#0A0F1A']}
      style={[styles.container, { borderColor: `${color}44` }]}
    >
      <View style={styles.header}>
        <View style={[styles.iconWrapper, { backgroundColor: `${color}22` }]}>
          <FontAwesome name={icon} size={15} color={color} />
        </View>
        <Text style={styles.title}>{title}</Text>
      </View>

      <View style={styles.valueRow}>
        <Text style={[styles.value, { color }]}>{value}</Text>
        <Text style={styles.subValue}>{subValue}</Text>
      </View>

      <View style={styles.progressBg}>
        <LinearGradient
          colors={accentGradient}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 0 }}
          style={[styles.progressFill, { width: `${Math.min(100, Math.max(0, percentage))}%` }]}
        />
      </View>
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    marginHorizontal: 4,
    marginVertical: 4,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  iconWrapper: {
    width: 26,
    height: 26,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 6,
  },
  title: {
    color: COLORS.textSub,
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  valueRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  value: {
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: 0.5,
  },
  subValue: {
    fontSize: 11,
    color: COLORS.textMuted,
    fontWeight: '600',
  },
  progressBg: {
    height: 5,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 4,
  },
});