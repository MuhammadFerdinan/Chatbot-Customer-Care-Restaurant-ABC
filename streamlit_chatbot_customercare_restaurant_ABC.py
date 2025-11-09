import streamlit as st
import random
import time

# --- 1. & 2. Data Menu Makanan dan Minuman ---
# Data random sederhana untuk simulasi
MENU_MAKANAN = {
    "Nasi Goreng Spesial": {"harga": 35000, "deskripsi": "Nasi goreng dengan bumbu rahasia, telur, dan irisan ayam."},
    "Mie Ayam Bakso": {"harga": 28000, "deskripsi": "Mie yang kenyal dengan topping ayam lezat dan bakso sapi."},
    "Sate Lilit Ayam": {"harga": 45000, "deskripsi": "Sate lilit khas Bali dengan sambal matah segar."},
    "Burger Klasik": {"harga": 40000, "deskripsi": "Roti bun lembut dengan patty daging sapi, keju, dan sayuran."},
}

MENU_MINUMAN = {
    "Es Teh Manis": {"harga": 10000, "deskripsi": "Teh hitam dingin yang menyegarkan."},
    "Kopi Latte Dingin": {"harga": 25000, "deskripsi": "Espresso dengan susu dan es, rasa klasik."},
    "Jus Alpukat": {"harga": 20000, "deskripsi": "Jus buah alpukat segar dengan sedikit cokelat."},
    "Air Mineral": {"harga": 5000, "deskripsi": "Air putih kemasan dingin."},
}

# --- 4. Metode Pembayaran ---
METODE_PEMBAYARAN = [
    "Transfer ATM Bank",
    "Mobile Banking",
    "Virtual Account Bank",
    "OVO",
    "Gopay",
    "Dana",
]

# --- 5. Metode Pengiriman ---
METODE_PENGIRIMAN = [
    "Diambil di Tempat (Take Away)",
    "Dikirim via GoFood (Biaya kirim ditanggung pembeli)",
]

# --- Fungsi Bantuan ---

def get_menu_text():
    """Mengembalikan teks menu lengkap."""
    makanan_list = "\n".join([
        f"- **{nama}** (Rp {data['harga']:,}): {data['deskripsi']}"
        for nama, data in MENU_MAKANAN.items()
    ])
    minuman_list = "\n".join([
        f"- **{nama}** (Rp {data['harga']:,}): {data['deskripsi']}"
        for nama, data in MENU_MINUMAN.items()
    ])

    menu_text = (
        "🍽️ **DAFTAR MENU MAKANAN**\n"
        f"{makanan_list}\n\n"
        "🍹 **DAFTAR MENU MINUMAN**\n"
        f"{minuman_list}\n\n"
        "Silakan sebutkan nama menu dan jumlah yang ingin Anda pesan. \n"
        "Contoh: 'Pesan Nasi Goreng Spesial 1 dan Kopi Latte Dingin 2'."
    )
    return menu_text

def parse_order(prompt):
    """Logika sederhana untuk mencoba mengekstrak pesanan dari prompt."""
    semua_menu = {k.lower(): k for k in list(MENU_MAKANAN.keys()) + list(MENU_MINUMAN.keys())}
    pesanan_baru = {}
    
    # Coba identifikasi menu dan jumlah
    for keyword_lower, keyword_original in semua_menu.items():
        # Asumsi user menyebutkan angka sebelum atau sesudah nama menu
        parts = prompt.lower().split()
        
        try:
            # Cari nama menu di dalam prompt
            if keyword_lower in prompt.lower():
                # Coba cari angka di sekitar nama menu
                index = parts.index(keyword_lower.split()[0]) # Ambil kata pertama menu
                
                # Cek kata sebelumnya
                if index > 0 and parts[index-1].isdigit():
                    jumlah = int(parts[index-1])
                    pesanan_baru[keyword_original] = pesanan_baru.get(keyword_original, 0) + jumlah
                    
                # Cek kata setelahnya (jika tidak ada angka sebelumnya)
                elif index < len(parts) - 1 and parts[index+1].isdigit():
                    jumlah = int(parts[index+1])
                    pesanan_baru[keyword_original] = pesanan_baru.get(keyword_original, 0) + jumlah

        except ValueError:
            continue # Lanjut ke menu berikutnya

    return pesanan_baru

def calculate_total(pesanan):
    """Menghitung total harga pesanan."""
    total = 0
    for nama, jumlah in pesanan.items():
        if nama in MENU_MAKANAN:
            total += MENU_MAKANAN[nama]['harga'] * jumlah
        elif nama in MENU_MINUMAN:
            total += MENU_MINUMAN[nama]['harga'] * jumlah
    return total

def checkout_summary(pesanan, metode_kirim, total):
    """Membuat ringkasan checkout."""
    summary = "🧾 **RINGKASAN PESANAN**\n\n"
    summary += "*Metode Pengiriman: " + metode_kirim + "*\n\n"
    
    items = []
    for nama, jumlah in pesanan.items():
        harga_satuan = 0
        if nama in MENU_MAKANAN:
            harga_satuan = MENU_MAKANAN[nama]['harga']
        elif nama in MENU_MINUMAN:
            harga_satuan = MENU_MINUMAN[nama]['harga']
            
        harga_subtotal = harga_satuan * jumlah
        items.append(f"- **{nama}** ({jumlah}x @ Rp {harga_satuan:,}) = Rp {harga_subtotal:,}")

    summary += "\n".join(items)
    summary += f"\n\n**TOTAL HARGA: Rp {total:,}**"
    summary += "\n\nSelanjutnya, silakan pilih **Metode Pembayaran** yang Anda inginkan dari daftar di bawah."
    return summary

# --- Konfigurasi Streamlit ---

st.set_page_config(page_title="Chatbot Customer Care Restaurant ABC", layout="centered")
st.title("🍽️ Chatbot Customer Care Restaurant ABC")
st.markdown("Halo! Saya asisten virtual Anda. Bagaimana saya bisa membantu hari ini? Anda bisa ketik **'Menu'** untuk melihat daftar menu kami.")

# Inisialisasi state sesi
if "messages" not in st.session_state:
    st.session_state.messages = []
if "order" not in st.session_state:
    st.session_state.order = {} # Format: {"Nama Menu": Jumlah}
if "state" not in st.session_state:
    st.session_state.state = "start" # start, order_received, delivery_chosen, payment_chosen

# Tampilkan riwayat pesan
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Logika Chatbot ---

if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tambahkan pesan pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Logika respons
    with st.chat_message("assistant"):
        response = ""
        
        # --- Cek State saat ini ---
        
        if st.session_state.state == "start":
            if "menu" in prompt.lower():
                response = get_menu_text()
                st.session_state.state = "viewing_menu"
            else:
                response = "Saya bisa membantu Anda dengan **Daftar Menu**, **Pemesanan**, atau info **Kontak** restoran. Silakan ketik 'Menu' jika Anda ingin memesan."
            
        elif st.session_state.state == "viewing_menu" or st.session_state.state == "order_received":
            # Coba proses pesanan
            pesanan_baru = parse_order(prompt)
            
            if pesanan_baru:
                # Gabungkan pesanan baru ke pesanan saat ini
                for item, qty in pesanan_baru.items():
                    st.session_state.order[item] = st.session_state.order.get(item, 0) + qty

                # Ringkasan pesanan saat ini
                current_order_summary = "\n".join([f"- {nama} x{jumlah}" for nama, jumlah in st.session_state.order.items()])
                total = calculate_total(st.session_state.order)

                response = (
                    "✅ **Pesanan saat ini:**\n"
                    f"{current_order_summary}\n\n"
                    f"**Total sementara: Rp {total:,}**\n\n"
                    "Apakah ada menu lain yang ingin ditambahkan, atau Anda ingin **'Checkout'** sekarang?"
                )
                st.session_state.state = "order_received"
                
            elif "checkout" in prompt.lower() and st.session_state.order:
                # --- 3. Checkout ---
                response = (
                    "🛒 Baik, mari kita proses checkout. \n\n"
                    "**Silakan pilih metode pengiriman Anda:**\n"
                    f"- {METODE_PENGIRIMAN[0]}\n"
                    f"- {METODE_PENGIRIMAN[1]}\n\n"
                    "Ketik pilihan Anda (Contoh: 'Diambil di Tempat' atau 'GoFood')."
                )
                st.session_state.state = "choosing_delivery"
            
            elif "checkout" in prompt.lower() and not st.session_state.order:
                response = "Anda belum menambahkan apa pun ke keranjang. Silakan pesan dulu dari menu!"
            
            else:
                response = "Mohon maaf, saya belum mengerti pesanan Anda. Pastikan Anda menyebutkan nama menu dan jumlah (misal: '2 Nasi Goreng Spesial')."

        # --- 5. Metode Pengiriman ---
        elif st.session_state.state == "choosing_delivery":
            selected_delivery = None
            for method in METODE_PENGIRIMAN:
                if method.lower() in prompt.lower() or method.split()[0].lower() in prompt.lower():
                    selected_delivery = method
                    break
            
            if selected_delivery:
                st.session_state.delivery_method = selected_delivery
                total = calculate_total(st.session_state.order)
                
                # Tampilkan Ringkasan & minta Metode Pembayaran
                summary_text = checkout_summary(st.session_state.order, selected_delivery, total)
                response = summary_text
                
                # Tampilkan opsi pembayaran
                payment_options = "\n".join([f"- {i+1}. {method}" for i, method in enumerate(METODE_PEMBAYARAN)])
                response += f"\n\n**Opsi Pembayaran:**\n{payment_options}"
                response += "\n\nKetik nomor atau nama metode pembayaran yang Anda pilih."
                
                st.session_state.state = "choosing_payment"
            else:
                response = "Pilihan pengiriman tidak valid. Silakan ketik 'Diambil di Tempat' atau 'Dikirim via GoFood'."
                
        # --- 4. Metode Pembayaran ---
        elif st.session_state.state == "choosing_payment":
            selected_payment = None
            
            # Coba identifikasi berdasarkan nomor
            try:
                pilihan_index = int(prompt.split()[0]) - 1
                if 0 <= pilihan_index < len(METODE_PEMBAYARAN):
                    selected_payment = METODE_PEMBAYARAN[pilihan_index]
            except:
                pass
            
            # Coba identifikasi berdasarkan nama
            if not selected_payment:
                for method in METODE_PEMBAYARAN:
                    if method.lower() in prompt.lower():
                        selected_payment = method
                        break
            
            if selected_payment:
                st.session_state.payment_method = selected_payment
                total = calculate_total(st.session_state.order)
                
                response = (
                    "🎉 **PESANAN SELESAI!** 🎉\n\n"
                    f"Pesanan Anda telah dicatat dengan rincian:\n"
                    f"- **Total:** Rp {total:,}\n"
                    f"- **Pengiriman:** {st.session_state.delivery_method}\n"
                    f"- **Pembayaran:** {selected_payment}\n\n"
                    "Silakan lakukan pembayaran sesuai metode yang dipilih.\n\n"
                    "*Terima kasih telah memesan di Restaurant ABC!*\n\n"
                    "Ketik **'Ulangi'** untuk memulai pesanan baru."
                )
                st.session_state.state = "order_completed"
                
            else:
                response = "Pilihan pembayaran tidak valid. Silakan ketik nomor (1-6) atau nama metode pembayaran yang benar."

        elif st.session_state.state == "order_completed":
            if "ulangi" in prompt.lower():
                # Reset semua state
                st.session_state.order = {}
                st.session_state.state = "start"
                st.session_state.messages = []
                response = "👋 Sistem telah diatur ulang. Silakan ketik **'Menu'** untuk memulai pesanan baru!"
                st.rerun() # Refresh tampilan
            else:
                response = "Pesanan sudah selesai. Jika ada pertanyaan lain, silakan ketik. Atau ketik **'Ulangi'** untuk memulai pesanan baru."


        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Catatan: Untuk menjalankan kode ini, Anda perlu menginstal Streamlit:
# pip install streamlit
# Kemudian jalankan dari terminal:
# streamlit run chatbot_restoran.py