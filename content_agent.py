import json
import random

class ContentAgent:
    def __init__(self, client):
        self.client = client
        
        self.niche_prompts = {
            "mysterious_events": "gizemli kayıp olayları, açıklanamayan fenomenler, terk edilmiş yerler",
            "conspiracy_theories": "hükümet sırları, tarihin karanlık yüzü, gizlenen gerçekler",
            "disaster_scenarios": "simülasyon teorisi, paralel evren, AI takeover, felaket senaryoları",
            "leaked_footage": "sızdırılmış belgeler, gizli kayıtlar, whistleblower hikayeleri"
        }

    def generate_video(self, niche: str, analytics_data: dict) -> dict:
        # Analytics'ten öğrendiklerini prompt'a ekle
        performance_insight = self._get_performance_insight(analytics_data)
        niche_description = self.niche_prompts.get(niche, self.niche_prompts["mysterious_events"])
        
        prompt = f"""Sen viral YouTube videoları için içerik üreten bir uzmansın.
        
Niş: {niche_description}
Dil: İngilizce (global kitle)
Format: Faceless video (yüz göstermeden, sadece görsel + seslendirme)

Performans verilerinden öğrendiklerimiz:
{performance_insight}

Aşağıdaki formatta bir video içeriği üret:

1. BAŞLIK: Merak uyandıran, tıklanma oranı yüksek (50 karakter max)
2. HOOK (ilk 15 saniye): İzleyiciyi anında yakalayacak açılış cümlesi
3. SCRIPT: 3-4 dakikalık video scripti (bölümlere ayır)
4. GÖRSEL AÇIKLAMALAR: Her bölüm için hangi görsellerin kullanılacağı
5. TAGS: 15 adet YouTube SEO tag
6. DESCRIPTION: 200 kelimelik video açıklaması
7. THUMBNAIL KAVRAMI: Thumbnail'de ne olmalı

Önemli: Gerçekmiş gibi hissettiren ama eğlenceli, dramatik bir ton kullan.
Yanıtını JSON formatında ver."""

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # JSON parse et
        content = response.content[0].text
        
        # JSON bloğunu temizle
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        try:
            video_data = json.loads(content)
        except:
            # Parse edilemezse manuel oluştur
            video_data = {
                "title": "The Mystery Nobody Talks About",
                "hook": "What you're about to see will change everything you think you know...",
                "script": content,
                "visual_descriptions": ["Dark mysterious atmosphere", "Old documents", "Strange symbols"],
                "tags": ["mystery", "conspiracy", "unexplained", "secrets", "viral"],
                "description": "Exploring the mysteries that mainstream media won't cover.",
                "thumbnail_concept": "Dark background with glowing eye symbol"
            }
        
        video_data["niche"] = niche
        return video_data

    def _get_performance_insight(self, analytics_data: dict) -> str:
        if not analytics_data or analytics_data.get("status") == "no_data":
            return "Henüz yeterli veri yok. Genel viral trendleri takip et."
        
        insights = []
        
        if analytics_data.get("best_performing_type"):
            insights.append(f"En çok izlenen içerik türü: {analytics_data['best_performing_type']}")
        
        if analytics_data.get("avg_watch_time"):
            insights.append(f"Ortalama izlenme süresi: {analytics_data['avg_watch_time']} saniye")
        
        if analytics_data.get("top_tags"):
            insights.append(f"En iyi performans gösteren taglar: {', '.join(analytics_data['top_tags'])}")
            
        return "\n".join(insights) if insights else "İlk videolar — genel viral format kullan."
