from core.audit_core import audit_text

def test_high_risk_word_detected():
    result = audit_text("这是最好的产品")
    assert result["is_safe"] is False
    risks = [r["word"] for r in result["risks"]]
    assert "最" in risks

def test_safe_text_passes():
    result = audit_text("今天天气不错")
    assert result["is_safe"] is True
    assert result["risks"] == []

def test_refined_content_replaces_word():
    result = audit_text("我们是第一")
    assert "第一" not in result["refined_content"]
    assert "业内深耕" in result["refined_content"] or "追求极致" in result["refined_content"]

def test_medium_risk_detected():
    result = audit_text("点击链接领取奖励")
    levels = [r["level"] for r in result["risks"]]
    assert "MEDIUM" in levels
