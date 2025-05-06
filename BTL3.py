import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Đọc dữ liệu
df = pd.read_csv("premier_league_players_full.csv")

# Lọc các cột số học
numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
df_numeric = df[numeric_cols].dropna()  # Loại bỏ các hàng có giá trị thiếu

# Chuẩn hóa dữ liệu
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_numeric)

#Tìm số cụm tối ưu với Elbow Method
inertias = []
k_range = range(1, 11)

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(df_scaled)
    inertias.append(kmeans.inertia_)

plt.figure(figsize=(8, 4))
plt.plot(k_range, inertias, marker='o')
plt.title("Elbow Method for Optimal k")
plt.xlabel("Number of clusters (k)")
plt.ylabel("Inertia")
plt.grid(True)
plt.tight_layout()
plt.savefig("elbow_plot.png")
plt.show()

#Tính Silhouette Score để tham khảo
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(df_scaled)
    score = silhouette_score(df_scaled, labels)

#Áp dụng KMeans với số cụm tối ưu
optimal_k = 3  # Có thể thay đổi sau khi xem biểu đồ Elbow và Silhouette
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
clusters = kmeans.fit_predict(df_scaled)
df['Cluster'] = clusters

# ======= Giảm chiều dữ liệu với PCA =======
pca = PCA(n_components=2)
reduced_data = pca.fit_transform(df_scaled)
df['PCA1'] = reduced_data[:, 0]
df['PCA2'] = reduced_data[:, 1]

# ======= Vẽ biểu đồ phân cụm 2D =======
plt.figure(figsize=(10, 6))
scatter = plt.scatter(df['PCA1'], df['PCA2'], c=df['Cluster'], cmap='Set1', alpha=0.7)

# Thêm nhãn cụm
for i in range(optimal_k):
    cluster_center = df[df['Cluster'] == i][['PCA1', 'PCA2']].mean()
    plt.text(cluster_center['PCA1'], cluster_center['PCA2'], f'Cluster {i}', fontsize=12, weight='bold')

plt.title(f"K-means Clustering with PCA (k = {optimal_k})")
plt.xlabel("PCA 1")
plt.ylabel("PCA 2")
plt.colorbar(scatter, label='Cluster')
plt.grid(True)
plt.tight_layout()
plt.savefig("cluster_pca_plot.png")
plt.show()

#Lưu kết quả
df.to_csv("clusters_with_pca.csv", index=False)

