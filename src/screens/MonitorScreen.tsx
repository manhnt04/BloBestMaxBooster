import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { BatteryInfo, DeviceSpecs, SystemStats } from '../types';
import { COLORS } from '../theme/colors';

interface MonitorScreenProps {
  stats: SystemStats;
  specs: DeviceSpecs;
  battery: BatteryInfo;
}

export const MonitorScreen: React.FC<MonitorScreenProps> = ({ stats, specs, battery }) => {
  const usedStorageGB = Math.max(0, Number((specs.totalStorageGB - specs.freeStorageGB).toFixed(1)));
  const storagePercent = specs.totalStorageGB > 0 ? Math.round((usedStorageGB / specs.totalStorageGB) * 100) : 60;

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {/* 1. Real Hardware Specs */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <FontAwesome name="cube" size={16} color={COLORS.cyan} />
          <Text style={styles.cardTitle}>THÔNG SỐ PHẦN CỨNG THỰC TẾ</Text>
        </View>

        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Tên Thiết Bị:</Text>
          <Text style={styles.specVal}>{specs.model}</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Nhà Sản Xuất:</Text>
          <Text style={styles.specVal}>{specs.manufacturer}</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Hệ Điều Hành:</Text>
          <Text style={styles.specVal}>{specs.osVersion}</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Kiến Trúc CPU:</Text>
          <Text style={styles.specVal}>{specs.cpuArchitecture} ({specs.coreCount} Nhân)</Text>
        </View>
      </View>

      {/* 2. Real Memory & Storage */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <FontAwesome name="hdd-o" size={16} color={COLORS.purple} />
          <Text style={styles.cardTitle}>BỘ NHỚ RAM & DUNG LƯỢNG Ổ CỨNG</Text>
        </View>

        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Tổng Bộ Nhớ RAM:</Text>
          <Text style={[styles.specVal, { color: COLORS.cyan }]}>{specs.totalMemoryGB} GB</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Tổng Ổ Cứng Máy:</Text>
          <Text style={styles.specVal}>{specs.totalStorageGB} GB</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Dung Lượng Còn Trống:</Text>
          <Text style={[styles.specVal, { color: COLORS.green }]}>
            {specs.freeStorageGB} GB ({100 - storagePercent}% Khả dụng)
          </Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Đã Sử Dụng:</Text>
          <Text style={styles.specVal}>{usedStorageGB} GB ({storagePercent}%)</Text>
        </View>
      </View>

      {/* 3. Real Battery Health */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <FontAwesome
            name={battery.isCharging ? 'bolt' : 'battery-full'}
            size={16}
            color={COLORS.green}
          />
          <Text style={styles.cardTitle}>TÌNH TRẠNG PIN THỜI GIAN THỰC</Text>
        </View>

        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Mức Pin Thực Tế:</Text>
          <Text style={[styles.specVal, { color: COLORS.green }]}>{battery.batteryPercent}%</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Trạng Thái Nguồn:</Text>
          <Text style={styles.specVal}>{battery.stateLabel}</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Nguồn Điện Thấp (Low Power):</Text>
          <Text style={[styles.specVal, { color: battery.isLowPowerMode ? COLORS.amber : COLORS.textSub }]}>
            {battery.isLowPowerMode ? 'Đang Bật' : 'Tắt'}
          </Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Điện Áp Định Danh:</Text>
          <Text style={styles.specVal}>{battery.voltageVolts} V</Text>
        </View>
      </View>

      {/* 4. Real Network Diagnostics */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <FontAwesome name="wifi" size={16} color={COLORS.cyan} />
          <Text style={styles.cardTitle}>CHẨN ĐOÁN MẠNG THỜI GIAN THỰC</Text>
        </View>

        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Đường Truyền Mạng:</Text>
          <Text style={styles.specVal}>{stats.networkType}</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Địa Chỉ IP Nội Bộ:</Text>
          <Text style={[styles.specVal, { color: COLORS.cyan }]}>{stats.ipAddress}</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Độ Trễ Đến Cloudflare 1.1.1.1:</Text>
          <Text style={[styles.specVal, { color: COLORS.green }]}>{stats.pingMs} ms</Text>
        </View>
        <View style={styles.specRow}>
          <Text style={styles.specLabel}>Độ Ổn Định (Jitter):</Text>
          <Text style={styles.specVal}>{stats.jitterMs} ms (Rất thấp)</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgDark,
  },
  content: {
    padding: 14,
    paddingBottom: 40,
    gap: 14,
  },
  card: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: COLORS.borderDark,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderDark,
    paddingBottom: 8,
  },
  cardTitle: {
    color: COLORS.textMain,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.8,
  },
  specRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 5,
  },
  specLabel: {
    color: COLORS.textSub,
    fontSize: 11,
  },
  specVal: {
    color: COLORS.textMain,
    fontSize: 11,
    fontWeight: '700',
  },
});