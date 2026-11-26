from engine.production import make_story


def test_story_generated_for_topic():
    topic={'id':'X','title':'Cara belajar AI','angle':'latihan prompt bertahap'}
    s=make_story(topic)
    assert 650 <= len(s.narration()) <= 800
    assert 'AI' in s.narration()
