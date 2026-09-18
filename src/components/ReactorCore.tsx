import React, { useEffect, useRef } from 'react';
import { Animated, Easing, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { FontAwesome } from '@expo/vector-icons';
import { COLORS } from '../theme/colors';

interface ReactorCoreProps {
  isBoosted: boolean;
  onPressBoost: () => void;
  fpsEstimate: number;
}

export const ReactorCore: React.FC<ReactorCoreProps> = ({
  isBoosted,
  onPressBoost,
  fpsEstimate,
}) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Pulse animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.05,
          duration: 1200,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1200,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Rotate animation
    Animated.loop(
      Animated.timing(rotateAnim, {
        toValue: 1,
        duration: 16000,
        easing: Easing.linear,
        useNativeDriver: true,
      })
    ).start();
  }, []);

  const spin = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.wrapper}>
      {/* Outer Rotating Cyber Tech Ring */}
      <Animated.View style={[styles.outerRing, { transform: [{ rotate: spin }] }]}>
        <View style={[styles.ringTick, { top: -2, alignSelf: 'center' }]} />
        <View style={[styles.ringTick, { bottom: -2, alignSelf: 'center' }]} />
        <View style={[styles.ringTick, { left: -2, top: '50%' }]} />
        <View style={[styles.ringTick, { right: -2, top: '50%' }]} />
      </Animated.View>

      {/* Pulsing Core Button */}
      <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
        <TouchableOpacity activeOpacity={0.85} onPress={onPressBoost} style={styles.touchArea}>
          <LinearGradient
            colors={isBoosted ? ['#00F2FE', '#4FACFE', '#7F00FF'] : ['#FF416C', '#FF4B2B', '#8E2DE2']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.reactorButton}
          >
            <View style={styles.innerGlass}>
              <FontAwesome
                name={isBoosted ? 'bolt' : 'rocket'}
                size={34}
                color={isBoosted ? COLORS.cyan : '#FFF'}
              />
              <Text style={styles.boostTitle}>
                {isBoosted ? 'HYPER BOOST' : 'TĂNG TỐC'}
              </Text>
              <Text style={styles.fpsText}>
                {fpsEstimate} <Text style={styles.fpsUnit}>FPS MƯỢT</Text>
              </Text>
              <View style={styles.subStatusBadge}>
                <Text style={styles.subStatusText}>
                  {isBoosted ? '✦ ĐÃ TỐI ƯU CỰC ĐẠI' : 'CHẠM ĐỂ KÍCH HOẠT'}
                </Text>
              </View>
            </View>
          </LinearGradient>
        </TouchableOpacity>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 18,
    position: 'relative',
  },
  outerRing: {
    position: 'absolute',
    width: 210,
    height: 210,
    borderRadius: 105,
    borderWidth: 1.5,
    borderColor: 'rgba(0, 242, 254, 0.25)',
    borderStyle: 'dashed',
  },
  ringTick: {
    position: 'absolute',
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.cyan,
  },
  touchArea: {
    borderRadius: 95,
    padding: 6,
  },
  reactorButton: {
    width: 178,
    height: 178,
    borderRadius: 89,
    padding: 4,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: COLORS.cyan,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.6,
    shadowRadius: 18,
    elevation: 10,
  },
  innerGlass: {
    width: '100%',
    height: '100%',
    borderRadius: 85,
    backgroundColor: 'rgba(10, 14, 26, 0.88)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
  },
  boostTitle: {
    color: COLORS.textMain,
    fontSize: 16,
    fontWeight: '900',
    letterSpacing: 1.5,
    marginTop: 6,
  },
  fpsText: {
    color: COLORS.cyan,
    fontSize: 17,
    fontWeight: '900',
    marginTop: 2,
  },
  fpsUnit: {
    fontSize: 10,
    color: COLORS.textSub,
    fontWeight: '600',
  },
  subStatusBadge: {
    marginTop: 6,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
  },
  subStatusText: {
    color: COLORS.textSub,
    fontSize: 9,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});