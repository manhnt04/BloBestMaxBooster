import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { COLORS } from '../theme/colors';

interface HeaderHUDProps {
  battery: number;
  isBoosted: boolean;
  deviceName?: string;
  networkType?: string;
  isCharging?: boolean;
}

export const HeaderHUD: React.FC<HeaderHUDProps> = ({
  battery,
  isBoosted,
  deviceName = 'IPHONE',
  networkType = 'WI-FI 5G',
  isCharging = false,
}) => {
  const [timeStr, setTimeStr] = useState('');

  useEffect(() => {
    const update = () => {
      const d = new Date();
      const h = String(d.getHours()).padStart(2, '0');
      const m = String(d.getMinutes()).padStart(2, '0');
      setTimeStr(`${h}:${m}`);
    };
    update();
    const timer = setInterval(update, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <View style={styles.container}>
      <View style={styles.deviceRow}>
        <View style={styles.glowDot} />
        <Text style={styles.deviceText} numberOfLines={1}>
          {deviceName.toUpperCase()}
        </Text>
        <View style={[styles.statusBadge, isBoosted ? styles.badgeBoosted : styles.badgeNormal]}>
          <Text style={styles.statusBadgeText}>
            {isBoosted ? '⚡ HYPER TURBO' : 'CHUẨN BỊ'}
          </Text>
        </View>
      </View>

      <View style={styles.metricsRow}>
        <View style={styles.metricItem}>
          <FontAwesome
            name={isCharging ? 'bolt' : 'battery-3'}
            size={13}
            color={isCharging ? COLORS.amber : COLORS.green}
          />
          <Text style={styles.metricText}>{battery}%</Text>
        </View>
        <View style={styles.metricDivider} />
        <View style={styles.metricItem}>
          <FontAwesome name="wifi" size={13} color={COLORS.cyan} />
          <Text style={styles.metricText} numberOfLines={1}>{networkType.toUpperCase()}</Text>
        </View>
        <View style={styles.metricDivider} />
        <View style={styles.metricItem}>
          <FontAwesome name="clock-o" size={13} color={COLORS.textSub} />
          <Text style={styles.metricText}>{timeStr}</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingTop: 8,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderDark,
    backgroundColor: COLORS.bgDarker,
  },
  deviceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  glowDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.cyan,
    marginRight: 8,
    shadowColor: COLORS.cyan,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 1,
    shadowRadius: 6,
    elevation: 4,
  },
  deviceText: {
    color: COLORS.textMain,
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 1.2,
    flex: 1,
    marginRight: 8,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeBoosted: {
    backgroundColor: 'rgba(0, 242, 254, 0.15)',
    borderWidth: 1,
    borderColor: COLORS.cyan,
  },
  badgeNormal: {
    backgroundColor: 'rgba(148, 163, 184, 0.15)',
    borderWidth: 1,
    borderColor: COLORS.borderDark,
  },
  statusBadgeText: {
    color: COLORS.cyan,
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  metricsRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metricItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  metricText: {
    color: COLORS.textSub,
    fontSize: 11,
    fontWeight: '600',
  },
  metricDivider: {
    width: 1,
    height: 10,
    backgroundColor: COLORS.borderDark,
    marginHorizontal: 10,
  },
});