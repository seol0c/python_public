import sys
# 패키지 설치 경로 추가
# pip install --target=D:\seolgit\python_packages numpy matplotlib
# 위 명령으로 지정 폴더에 패키지 설치 후, sys.path.append로 경로를 파이썬에 알려줌
sys.path.append(r"D:\seolgit\python_packages")  # 패키지가 설치된 경로 지정

# 사용할 외부 패키지(설치함)
import numpy as np                  # 수치 계산 (배열, 지수함수 등)
import matplotlib.pyplot as plt     # 그래프 그리기

# -------------------------------
# 사용되는 기본 물리 상수 (SI 단위계)
# -------------------------------
h = 6.62607015e-34      # 플랑크 상수 [J·s]
c = 2.99792458e8        # 빛의 속도 [m/s]
k = 1.380649e-23        # 볼츠만 상수 [J/K]

# -------------------------------
# 플랑크의 복사 법칙 (에너지 밀도 표현)
# lam : 파장 [m]
# T   : 절대온도 [K]
# 반환값 : u_lambda [J·m^-4] (J/m^3 per m)
# -------------------------------
def u_lambda(lam, T):
    a = 8 * np.pi * h * c / (lam**5)
    b = h * c / (lam * k * T)
    return a / (np.exp(b) - 1)

# -------------------------------
# 계산할 파장 범위 설정
# -------------------------------
w_nm = np.linspace(0, 3000, 1000)   # 파장 (nm 단위)
lam = w_nm * 1e-9                   # m 단위 변환


# 그림 크기 지정 - 가로, 세로
fig, ax = plt.subplots(figsize=(5, 3))


# -------------------------------
# 여러 온도에서 흑체복사 곡선 (절대값) 그리기
# -------------------------------
temps = [2500, 3000, 3500, 4000, 4500, 5000, 5500]     # K
for T in temps:
    u = u_lambda(lam, T)             # [J m^-4]
    u_kJ_per_nm = u * 1e-12          # J→kJ(×1e-3), per m→per nm(×1e-9) ⇒ ×1e-12
    ax.plot(w_nm, u_kJ_per_nm, label=f"{T} K")

# -------------------------------
# Wien 꼭짓점(피크) 점 + 점선
# λ_max = b/T,  b ≈ 2.897771955×10^-3 m·K  (= 2.897771955×10^6 nm·K)
# -------------------------------
b_wien_mK  = 2.897771955e-3          # m·K
peak_x_nm  = []
peak_y_kjn = []
for T in temps:
    lam_max = b_wien_mK / T          # [m]
    x_nm    = lam_max * 1e9          # [nm]
    y_kjn   = u_lambda(lam_max, T) * 1e-12  # [kJ/nm]
    peak_x_nm.append(x_nm)
    peak_y_kjn.append(y_kjn)
    ax.plot(x_nm, y_kjn, "o", color="k", markersize=4)  # 꼭짓점 표시

ax.plot(peak_x_nm, peak_y_kjn, "k--", linewidth=1, label="Wien's law")

# -------------------------------
# 가시광선 범위 수직선 (380 nm, 750 nm)
# -------------------------------
ax.axvline(380, color="gray", linestyle=":", linewidth=1, label="Visible range")
ax.axvline(750, color="gray", linestyle=":", linewidth=1)

# -------------------------------
# 라벨/제목/범례
# -------------------------------
ax.set_xlabel("Wavelength (nm)", fontsize=10)
ax.set_ylabel(r"$u(\lambda)$ ($10^{-7}$ kJ/nm)", fontsize=10)  # 지수 포함 라벨(숫자는 그대로)
ax.set_title("Blackbody radiation", fontsize=10)
ax.legend(title="Temperature", loc="upper right", fontsize=10)
ax.tick_params(axis='both', labelsize=10)        # 눈금 폰트

# 온도 범례를 뒤집음(고온이 위로 가도록)
# 현재 모든 범례 항목 가져오기
handles, labels = ax.get_legend_handles_labels()

# 온도 라인만 (끝에서 2개는 Wien's law, Visible range)
temp_handles = handles[:-2][::-1]   # 역순 (고온이 위)
temp_labels = labels[:-2][::-1]

# 추가 라인만
extra_handles = handles[-2:]
extra_labels = labels[-2:]

# 합치기 (온도 먼저, 그 다음 추가 라인)
new_handles = temp_handles + extra_handles
new_labels = temp_labels + extra_labels

# 범례 출력
ax.legend(new_handles, new_labels, title="", loc="upper right", fontsize=10)

# 원점이 꼭짓점에 붙도록 설정
ax.set_xlim(0, 3000)    # x축 0~3000 nm
ax.set_ylim(0, None)    # y축 0부터 시작
ax.margins(x=0, y=0)    # x, y축 여백 제거
ax.yaxis.get_offset_text().set_visible(False)  # 축 위쪽 1e-? 표시 제거

plt.tight_layout()

# 0 눈금 라벨 숨기기 (x, y 모두)
xt = ax.get_xticks(); ax.set_xticks([t for t in xt if t != 0])
yt = ax.get_yticks(); ax.set_yticks([t for t in yt if t != 0])
# 원점에 '0'을 한 번만 표시
ax.annotate("0", xy=(0, 0), xycoords="data",
            xytext=(-8, -8), textcoords="offset points",
            ha="center", va="center", clip_on=False)

# -------------------------------
# 결과 저장 (벡터) - 비활성화하고 수동으로 저장
# -------------------------------
# plt.savefig("blackbody_u_lambda.svg")
# plt.savefig("blackbody_u_lambda.pdf") 

# -------------------------------
# 화면 출력
# -------------------------------
plt.show()