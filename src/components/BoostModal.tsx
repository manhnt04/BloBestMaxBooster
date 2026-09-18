import React, { useEffect, useState } from 'react';
import { Modal, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome } from '@expo/vector-icons';
import { BoostBenchmarkResult } from '../types';
import { COLORS } from '../theme/colors';

interface BoostModalProps {
  visible: boolean;
  benchmark: BoostBenchmarkResult | null;
  onClose: () => void;
}

export const BoostModal: React.FC<BoostModalProps> = ({ visible, benchmark, onClose }) => {
  const [step, setStep] = useState(0);
  const [isDone, setIsDone] = useState(false);

  const steps = [
    '✦ Giải phóng bộ nhớ đệm Cache & Làm sạch tiến trình...',
    '✦ Thiết lập kết nối Socket Pre-warming tới DNS 1.1.1.1...',
    '✦ Tối ưu hóa chu kỳ hiển thị & Khóa xung nhịp Turbo...',
    '✦ Hoàn tất! Thiết bị đã sẵn sàng cho trận đấu.',
  ];

  useEffect(() => {
    if (visible) {
      setStep(0);
      setIsDone(false);
      const t1 = setTimeout(() => setStep(1), 500);
      const t2 = setTimeout(() => setStep(2), 1000);
      const t3 = setTimeout(() => setStep(3), 1500);
      const t4 = setTimeout(() => setIsDone(true), 2000);
      return () => {
        clearTimeout(t1);
        clearTimeout(t2);
        clearTimeout(t3);
        clearTimeout(t4);
      };
    }
  }, [visible]);

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={styles.overlay}>
        <LinearGradient colors={['#131B2E', '#090D18']} style={styles.card}>
          <View style={styles.header}>
            <View style={styles.iconCircle}>
              <FontAwesome
                name={isDone ? 'check-circle' : 'bolt'}
                size={32}
                color={isDone ? COLORS.green : COLORS.cyan}
              />
            </View>
            <Text style={styles.title}>
              {isDone ? 'ĐÃ TỐI ƯU SIÊU CẤP!' : 'ĐANG ĐO ĐẠC & TĂNG TỐC...'}
            </Text>
            <Text style={styles.subtitle}>
              {isDone
                ? `${benchmark?.deviceModel || 'Thiết bị'} • ${benchmark?.networkType || 'Mạng'}`
                : 'Đang kiểm tra độ trễ mạng thực tế và làm ấm kết nối'}
            </Text>
          </View>

          <View style={styles.stepsContainer}>
            {steps.map((text, idx) => {
              const active = step >= idx;
              return (
                <View key={idx} style={styles.stepRow}>
                  <FontAwesome
                    name={active ? 'check' : 'circle-o'}
                    size={13}
                    color={active ? COLORS.cyan : COLORS.textMuted}
                    style={{ marginRight: 8 }}
                  />
                  <Text style={[styles.stepText, active && styles.stepActive]}>
                    {text}
                  </Text>
                </View>
              );
            })}
          </View>

          {isDone && benchmark && (
            <View style={styles.statsSummary}>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryVal}>
                  {benchmark.pingAfterMs} ms
                </Text>
                <Text style={styles.summaryLabel}>PING THẬT (-{benchmark.pingDropMs}ms)</Text>
              </View>
              <View style={styles.summaryDiv} />
              <View style={styles.summaryItem}>
                <Text style={[styles.summaryVal, { color: COLORS.green }]}>
                  {benchmark.jitterMs} ms
                </Text>
                <Text style={styles.summaryLabel}>ĐỘ GIẬT (JITTER)</Text>
              </View>
              <View style={styles.summaryDiv} />
              <View style={styles.summaryItem}>
                <Text style={[styles.summaryVal, { color: COLORS.orange }]}>
                  {benchmark.freeStorageGB} GB
                </Text>
                <Text style={styles.summaryLabel}>BỘ NHỚ KHẢ DỤNG</Text>
              </View>
            </View>
          )}

          {isDone && (
            <TouchableOpacity activeOpacity={0.8} onPress={onClose} style={styles.closeBtn}>
              <LinearGradient
                colors={COLORS.reactorGrad}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.btnGrad}
              >
                <Text style={styles.closeBtnText}>VÀO TRẬN NGAY</Text>
              </LinearGradient>
            </TouchableOpacity>
          )}
        </LinearGradient>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(4, 6, 12, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  card: {
    width: '100%',
    borderRadius: 20,
    padding: 24,
    borderWidth: 1.5,
    borderColor: COLORS.cyan,
    shadowColor: COLORS.cyan,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  header: {
    alignItems: 'center',
    marginBottom: 16,
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: 'rgba(0, 242, 254, 0.12)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  title: {
    color: COLORS.textMain,
    fontSize: 18,
    fontWeight: '900',
    letterSpacing: 1,
    textAlign: 'center',
  },
  subtitle: {
    color: COLORS.textSub,
    fontSize: 11,
    textAlign: 'center',
    marginTop: 4,
  },
  stepsContainer: {
    marginVertical: 14,
    gap: 10,
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  stepText: {
    color: COLORS.textMuted,
    fontSize: 12,
  },
  stepActive: {
    color: COLORS.cyan,
    fontWeight: '700',
  },
  statsSummary: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.35)',
    borderRadius: 12,
    paddingVertical: 12,
    marginTop: 8,
    borderWidth: 1,
    borderColor: COLORS.borderDark,
  },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 2,
  },
  summaryVal: {
    color: COLORS.cyan,
    fontSize: 16,
    fontWeight: '900',
  },
  summaryLabel: {
    color: COLORS.textMuted,
    fontSize: 8,
    fontWeight: '800',
    marginTop: 3,
    textAlign: 'center',
  },
  summaryDiv: {
    width: 1,
    backgroundColor: COLORS.borderDark,
  },
  closeBtn: {
    marginTop: 18,
    borderRadius: 12,
    overflow: 'hidden',
  },
  btnGrad: {
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeBtnText: {
    color: '#000',
    fontWeight: '900',
    fontSize: 14,
    letterSpacing: 1.5,
  },
});