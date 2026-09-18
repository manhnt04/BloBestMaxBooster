import React, { useState } from 'react';
import { FlatList, Platform, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { ToolCard } from '../components/ToolCard';
import { NativeBoosterService } from '../services/nativeBooster';
import { GamingTool } from '../types';
import { COLORS } from '../theme/colors';

interface ToolsScreenProps {
  tools: GamingTool[];
  onToggleTool: (id: string, value: boolean) => void;
}

export const ToolsScreen: React.FC<ToolsScreenProps> = ({ tools, onToggleTool }) => {
  const [crosshairStyle, setCrosshairStyle] = useState('✦');
  const crosshairOptions = ['✦', '✛', '⊕', '⊙', '᛭', '✕'];

  return (
    <View style={styles.container}>
      {/* iOS Special Banner: Apple Game Focus Mode */}
      {Platform.OS === 'ios' && (
        <TouchableOpacity
          activeOpacity={0.85}
          onPress={() => NativeBoosterService.openIosGameFocusSettings()}
          style={styles.iosFocusBanner}
        >
          <View style={styles.iosFocusLeft}>
            <View style={styles.iosFocusIconCircle}>
              <FontAwesome name="moon-o" size={18} color="#FFF" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.iosFocusTitle}>CHẾ ĐỘ CHƠI GAME IOS (GAME FOCUS)</Text>
              <Text style={styles.iosFocusDesc}>
                Chạm để cấu hình tự động tắt thông báo & làm mới nền trên iPhone khi combat.
              </Text>
            </View>
          </View>
          <FontAwesome name="chevron-right" size={12} color={COLORS.cyan} />
        </TouchableOpacity>
      )}

      {/* Crosshair Customizer Section */}
      <View style={styles.crosshairBanner}>
        <View style={styles.crosshairHeader}>
          <Text style={styles.crosshairTitle}>🎯 TÂM ẢO NGẮM BẮN (FPS CROSSHAIR)</Text>
          <View style={styles.crosshairLivePreview}>
            <Text style={styles.crosshairLiveText}>{crosshairStyle}</Text>
          </View>
        </View>

        <Text style={styles.crosshairDesc}>
          {Platform.OS === 'ios'
            ? 'Bộ tâm ngắm chuẩn xác cho game thủ luyện phản xạ ngắm bắn không cần bật scope.'
            : 'Hiển thị tâm ngắm nổi đè lên trên game PUBG / Free Fire khi combat.'}
        </Text>

        <View style={styles.crosshairRow}>
          {crosshairOptions.map((opt) => {
            const isSelected = crosshairStyle === opt;
            return (
              <TouchableOpacity
                key={opt}
                onPress={() => setCrosshairStyle(opt)}
                style={[styles.crosshairBtn, isSelected && styles.crosshairBtnActive]}
              >
                <Text style={[styles.crosshairBtnText, isSelected && { color: COLORS.cyan }]}>
                  {opt}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      <Text style={styles.sectionHeader}>BỘ CÔNG CỤ CHUYÊN BIỆT</Text>

      <FlatList
        data={tools}
        numColumns={2}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <ToolCard tool={item} onToggle={onToggleTool} />
        )}
        contentContainerStyle={{ paddingBottom: 30 }}
        showsVerticalScrollIndicator={false}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bgDark,
    paddingHorizontal: 12,
    paddingTop: 12,
  },
  iosFocusBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#161F33',
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: 'rgba(0, 242, 254, 0.3)',
    marginBottom: 12,
  },
  iosFocusLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    flex: 1,
    marginRight: 8,
  },
  iosFocusIconCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#4FACFE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  iosFocusTitle: {
    color: COLORS.textMain,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  iosFocusDesc: {
    color: COLORS.textSub,
    fontSize: 10,
    marginTop: 2,
    lineHeight: 14,
  },
  crosshairBanner: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 14,
    padding: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 23, 68, 0.4)',
    marginBottom: 14,
  },
  crosshairHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  crosshairTitle: {
    color: COLORS.textMain,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  crosshairLivePreview: {
    width: 30,
    height: 30,
    borderRadius: 8,
    backgroundColor: 'rgba(255, 23, 68, 0.15)',
    borderWidth: 1,
    borderColor: COLORS.red,
    alignItems: 'center',
    justifyContent: 'center',
  },
  crosshairLiveText: {
    color: COLORS.red,
    fontSize: 16,
    fontWeight: '900',
  },
  crosshairDesc: {
    color: COLORS.textSub,
    fontSize: 10,
    lineHeight: 14,
    marginBottom: 8,
  },
  crosshairRow: {
    flexDirection: 'row',
    gap: 6,
  },
  crosshairBtn: {
    flex: 1,
    height: 34,
    borderRadius: 8,
    backgroundColor: '#090E1A',
    borderWidth: 1,
    borderColor: COLORS.borderDark,
    alignItems: 'center',
    justifyContent: 'center',
  },
  crosshairBtnActive: {
    borderColor: COLORS.cyan,
    backgroundColor: 'rgba(0, 242, 254, 0.15)',
  },
  crosshairBtnText: {
    color: COLORS.textMain,
    fontSize: 15,
    fontWeight: '700',
  },
  sectionHeader: {
    color: COLORS.textSub,
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 1.2,
    marginBottom: 8,
  },
});