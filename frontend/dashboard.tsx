"use client";

import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Button,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Chip,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  CircularProgress,
  Stack,
  Slider,
} from "@mui/material";
import {
  Search as SearchIcon,
  Video as VideoIcon,
  X as CloseIcon,
  ShieldAlert as AlertIcon,
  Sliders as FilterIcon,
  MapPin as PinIcon,
} from "lucide-react";

interface SearchEvent {
  event_id: string;
  score: number;
  primary_label: string;
  confidence: number;
  camera_name: string;
  site_id: string;
  started_at: string;
  snapshot_url: string;
  clip_url?: string;
  zones: string[];
}

export default function SurveillanceDashboard() {
  const [selectedSite, setSelectedSite] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [minScore, setMinScore] = useState<number>(0.2);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [results, setResults] = useState<SearchEvent[]>([]);
  const [activeClipModal, setActiveClipModal] = useState<SearchEvent | null>(null);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/search/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query_text: searchQuery,
          site_id: selectedSite === "all" ? null : selectedSite,
          limit: 24,
        }),
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#0f172a", color: "#f8fafc" }}>
      {/* Top Navbar */}
      <AppBar position="static" sx={{ bgcolor: "#1e293b", borderBottom: "1px solid #334155" }}>
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <AlertIcon size={24} color="#38bdf8" />
            <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: 0.5 }}>
              AIOTA <span style={{ color: "#38bdf8", fontSize: "0.85em" }}>VISION INTELLIGENCE</span>
            </Typography>
          </Stack>

          {/* Site Selector */}
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel sx={{ color: "#94a3b8" }}>Facility / Site</InputLabel>
            <Select
              value={selectedSite}
              label="Facility / Site"
              onChange={(e) => setSelectedSite(e.target.value)}
              sx={{ bgcolor: "#0f172a", color: "#f8fafc", ".MuiOutlinedInput-notchedOutline": { borderColor: "#334155" } }}
            >
              <MenuItem value="all">All Sites (Global)</MenuItem>
              <MenuItem value="site_farm_north">North Pasture (Farm A)</MenuItem>
              <MenuItem value="site_warehouse_02">Staging Yard (Logistics B)</MenuItem>
              <MenuItem value="site_construction_central">Main Gate (Construction Site 1)</MenuItem>
            </Select>
          </FormControl>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Search & Query Bar */}
        <Box component="form" onSubmit={handleSearch} sx={{ mb: 4 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={9}>
              <TextField
                fullWidth
                placeholder='Semantic Natural Language Search (e.g. "stray animal near gate", "worker without helmet", "forklift in aisle")'
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon size={20} color="#94a3b8" />
                    </InputAdornment>
                  ),
                  sx: {
                    bgcolor: "#1e293b",
                    color: "#f8fafc",
                    borderRadius: 2,
                    border: "1px solid #334155",
                    "& fieldset": { border: "none" },
                  },
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                fullWidth
                variant="contained"
                size="large"
                type="submit"
                disabled={isLoading}
                sx={{
                  bgcolor: "#0284c7",
                  height: 56,
                  borderRadius: 2,
                  fontWeight: 600,
                  "&:hover": { bgcolor: "#0369a1" },
                }}
              >
                {isLoading ? <CircularProgress size={24} color="inherit" /> : "Visual Search"}
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Results Grid */}
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="subtitle1" sx={{ color: "#94a3b8", fontWeight: 500 }}>
              Found {results.length} relevant detection events
            </Typography>
          </Stack>

          <Grid container spacing={3}>
            {results.map((event) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={event.event_id}>
                <Card
                  sx={{
                    bgcolor: "#1e293b",
                    color: "#f8fafc",
                    borderRadius: 2,
                    border: "1px solid #334155",
                    transition: "transform 0.2s, box-shadow 0.2s",
                    "&:hover": { transform: "translateY(-4px)", borderColor: "#38bdf8" },
                  }}
                >
                  <Box sx={{ position: "relative" }}>
                    <CardMedia
                      component="img"
                      height="180"
                      image={event.snapshot_url || "https://placehold.co/600x400/0f172a/94a3b8?text=No+Snapshot"}
                      alt={event.primary_label}
                    />
                    <Chip
                      label={`${(event.score * 100).toFixed(0)}% match`}
                      size="small"
                      sx={{
                        position: "absolute",
                        top: 8,
                        right: 8,
                        bgcolor: "rgba(2, 132, 199, 0.9)",
                        color: "#fff",
                        fontWeight: 600,
                      }}
                    />
                  </Box>

                  <CardContent sx={{ pb: 1 }}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="h6" sx={{ textTransform: "capitalize", fontSize: "1.05rem", fontWeight: 600 }}>
                        {event.primary_label}
                      </Typography>
                      <Chip
                        label={`${(event.confidence * 100).toFixed(0)}% conf`}
                        size="small"
                        variant="outlined"
                        sx={{ borderColor: "#475569", color: "#94a3b8", fontSize: "0.75rem" }}
                      />
                    </Stack>

                    <Stack direction="row" spacing={0.5} alignItems="center" sx={{ color: "#94a3b8", mb: 0.5 }}>
                      <PinIcon size={14} />
                      <Typography variant="body2" sx={{ fontSize: "0.8rem" }}>
                        {event.camera_name}
                      </Typography>
                    </Stack>

                    <Typography variant="caption" sx={{ color: "#64748b", display: "block" }}>
                      {new Date(event.started_at).toLocaleString()}
                    </Typography>

                    {event.zones.length > 0 && (
                      <Stack direction="row" spacing={0.5} sx={{ mt: 1 }}>
                        {event.zones.map((zone) => (
                          <Chip key={zone} label={zone} size="small" sx={{ bgcolor: "#334155", color: "#cbd5e1", fontSize: "0.7rem" }} />
                        ))}
                      </Stack>
                    )}
                  </CardContent>

                  <CardActions sx={{ px: 2, pb: 2 }}>
                    <Button
                      fullWidth
                      size="small"
                      variant="outlined"
                      startIcon={<VideoIcon size={16} />}
                      onClick={() => setActiveClipModal(event)}
                      disabled={!event.clip_url}
                      sx={{
                        borderColor: "#475569",
                        color: "#38bdf8",
                        "&:hover": { borderColor: "#38bdf8", bgcolor: "rgba(56, 189, 248, 0.05)" },
                      }}
                    >
                      {event.clip_url ? "Review Clip" : "No Clip Recorded"}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>

      {/* Video Clip Playback Modal */}
      <Dialog
        open={Boolean(activeClipModal)}
        onClose={() => setActiveClipModal(null)}
        maxWidth="md"
        fullWidth
        PaperProps={{ sx: { bgcolor: "#1e293b", color: "#f8fafc", borderRadius: 2 } }}
      >
        <DialogTitle sx={{ m: 0, p: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {activeClipModal?.camera_name}: {activeClipModal?.primary_label}
          </Typography>
          <IconButton onClick={() => setActiveClipModal(null)} sx={{ color: "#94a3b8" }}>
            <CloseIcon size={20} />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers sx={{ borderColor: "#334155", p: 0 }}>
          {activeClipModal?.clip_url ? (
            <video
              controls
              autoPlay
              style={{ width: "100%", maxHeight: "550px", display: "block", backgroundColor: "#000" }}
              src={activeClipModal.clip_url}
            />
          ) : (
            <Box sx={{ p: 4, textAlign: "center", color: "#94a3b8" }}>No video clip stream available.</Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
}
